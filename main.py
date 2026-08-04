import os
import json
import yaml
from core import (
    Module, 
    ValidatedExerciseSchema, 
    SlideDeckSchema, 
    ExerciseSolutionSchema, 
    UnitTestSchema,
    build_system_prompt, 
    build_slide_prompt, 
    build_exercise_prompt, 
    build_qa_prompt,
    get_instructor_client, 
    clean_code_snippet, 
    run_in_sandbox,
    build_pptx_deck,
    load_phase1_telemetry,
    formulate_problem_statement,
    ProblemStatementSchema
)

DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct"

def generate_curriculum(config_path: str = "test.yaml", output_dir: str = "outputs", telemetry_dir: str = "first_phase_outputs"):
    """Main curriculum generation execution pipeline with Agent 0 problem formulation."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    model_name = config.get("curriculum", {}).get("model") or config.get("model") or DEFAULT_MODEL_NAME
    print(f"[Pipeline Configuration] Using LLM Model: {model_name}")

    client = get_instructor_client()
    os.makedirs(output_dir, exist_ok=True)

    # Load Phase 1 Telemetry
    telemetry = load_phase1_telemetry(telemetry_dir)
    if telemetry:
        print(f"\n[Phase 1 Telemetry Loaded] Found metadata for dataset: {telemetry.get('run_summary', {}).get('config_file', 'dataset')}")

    for module_data in config["curriculum"]["modules"]:
        module = Module(**module_data)
        print(f"\n==================================================")
        print(f"Processing Module: {module.title} (Week {module.week})...")
        print(f"==================================================")
        
        # Step 0: Agent 0 - Problem Formulation Agent
        print(f"0. Agent 0: Formulating domain problem statement & Markdown overview from Phase 1 telemetry ({module.id})...")
        problem_formulation: ProblemStatementSchema = formulate_problem_statement(module, telemetry, client, model_name)
        print(f"   -> Formulated Title: {problem_formulation.title}")
        print(f"   -> Domain Directive: {problem_formulation.problem_statement[:120]}...")

        # Save Markdown Overview (.md)
        overview_path = os.path.join(output_dir, f"{module.id}_overview.md")
        with open(overview_path, "w", encoding="utf-8") as f:
            f.write(problem_formulation.markdown_overview if problem_formulation.markdown_overview else f"# {problem_formulation.title}\n\n{problem_formulation.problem_statement}")
        print(f"  -> Student Overview Document Saved to: {overview_path}")

        # Step A: Slide Deck Generation
        print(f"1. Fetching RAG context & building slides for {module.id}...")
        slide_prompt = build_slide_prompt(module, problem_formulation=problem_formulation)
        print(f"   -> Requesting Slide Deck from vLLM ({module.id})...")
        
        slide_deck: SlideDeckSchema = client.chat.completions.create(
            model=model_name,
            response_model=SlideDeckSchema,
            max_retries=3,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": slide_prompt}
            ]
        )
        
        # Save Slide Deck JSON
        slides_json_path = os.path.join(output_dir, f"{module.id}_slides.json")
        with open(slides_json_path, "w") as f:
            json.dump(slide_deck.model_dump(), f, indent=2)
            
        # Build PowerPoint (.pptx)
        pptx_path = os.path.join(output_dir, f"{module.id}_presentation.pptx")
        build_pptx_deck(slide_deck, pptx_path)
        print(f"  -> Slide Deck Generated & Saved to: {pptx_path}")

        # Step B1: Stage 1 - Generator Agent (Curriculum Code Educator)
        print(f"2. Generator Agent: Synthesizing PyTorch reference solution for {module.id}...")
        exercise_prompt = build_exercise_prompt(module, slide_deck=slide_deck, problem_formulation=problem_formulation)

        solution_result: ExerciseSolutionSchema = client.chat.completions.create(
            model=model_name,
            response_model=ExerciseSolutionSchema,
            max_retries=3,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": exercise_prompt}
            ]
        )

        # Step B2: Stage 2 - Adversarial QA Agent + Hybrid Sandbox Verification
        print(f"3. Adversarial QA Agent: Writing unit tests & running Hybrid Sandbox verification ({module.id})...")
        qa_prompt = build_qa_prompt(module, solution_result.solution_code, problem_formulation=problem_formulation)

        unit_test_result: UnitTestSchema = client.chat.completions.create(
            model=model_name,
            response_model=UnitTestSchema,
            max_retries=3,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": qa_prompt}
            ]
        )
        
        # Verify solution against unit test in sandbox
        success, log = run_in_sandbox(solution_result.solution_code, unit_test_result.unit_test)
        if not success:
            print(f"  -> Initial sandbox verification returned warnings/failures. Retrying QA Agent...")
            qa_retry_prompt = f"{qa_prompt}\n\n--- PREVIOUS SANDBOX VERIFICATION LOG ---\n{log}\n\nPlease fix the unit_test."
            unit_test_result = client.chat.completions.create(
                model=model_name,
                response_model=UnitTestSchema,
                max_retries=2,
                max_tokens=1500,
                messages=[
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": qa_retry_prompt}
                ]
            )
            success, log = run_in_sandbox(solution_result.solution_code, unit_test_result.unit_test)
            if not success:
                print(f"Warning: Sandbox verification returned log:\n{log}")

        exercise = ValidatedExerciseSchema.model_construct(
            title=solution_result.title,
            instructions=solution_result.instructions,
            starter_code=solution_result.starter_code,
            solution_code=solution_result.solution_code,
            unit_test=unit_test_result.unit_test
        )
        
        print(f"  -> GENERATION & VERIFICATION SUCCESS: {exercise.title}")

        clean_id = module.id.replace("-", "_")

        # JSON Metadata
        json_path = os.path.join(output_dir, f"{module.id}_generated.json")
        with open(json_path, "w") as f:
            json.dump(exercise.model_dump(), f, indent=2)

        # Starter Code (.py)
        exercise_path = os.path.join(output_dir, f"{clean_id}_exercise.py")
        with open(exercise_path, "w") as f:
            f.write(f'"""\n{exercise.title}\n\nInstructions:\n{exercise.instructions}\n"""\n\n')
            f.write(clean_code_snippet(exercise.starter_code) + "\n")

        # Solution Code (.py)
        solution_path = os.path.join(output_dir, f"{clean_id}_solution.py")
        with open(solution_path, "w") as f:
            f.write(f'"""\nSolution: {exercise.title}\n"""\n\n')
            f.write(clean_code_snippet(exercise.solution_code) + "\n")

        # Unit Test (.py)
        test_path = os.path.join(output_dir, f"{clean_id}_test.py")
        with open(test_path, "w") as f:
            f.write(f'"""\nUnit Tests: {exercise.title}\n"""\n\n')
            f.write(clean_code_snippet(exercise.unit_test) + "\n")

        print(f"Saved all module assets to '{output_dir}/':")
        print(f"  - {overview_path}")
        print(f"  - {slides_json_path}")
        print(f"  - {pptx_path}")
        print(f"  - {json_path}")
        print(f"  - {exercise_path}")
        print(f"  - {solution_path}")
        print(f"  - {test_path}")

if __name__ == "__main__":
    generate_curriculum()
