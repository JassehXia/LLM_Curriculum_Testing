import os
import json
import yaml
from schemas import Module, ValidatedExerciseSchema, SlideDeckSchema
from context import build_system_prompt, build_slide_prompt, build_exercise_prompt
from ai_setup import get_instructor_client
from sandbox import clean_code_snippet
from slide_builder import build_pptx_deck

def test_live_generation():
    # 1. Ingest test.yaml config
    with open("test.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # 2. Get Instructor Client
    client = get_instructor_client(base_url="http://localhost:8000/v1")
    
    # 3. Create outputs directory
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # 4. Iterate over ALL modules in the curriculum
    for module_data in config["curriculum"]["modules"]:
        module = Module(**module_data)
        print(f"\n==================================================")
        print(f"Processing Module: {module.title} (Week {module.week})...")
        print(f"==================================================")
        
        # Step A: Slide Deck Generation
        print(f"1. Generating Slide Deck Schema for {module.id}...")
        slide_deck: SlideDeckSchema = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            response_model=SlideDeckSchema,
            max_retries=3,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": build_slide_prompt(module)}
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

        # Step B: Sandbox-Validated Exercise Generation
        print(f"2. Generating Sandbox-Validated Exercise for {module.id}...")
        exercise: ValidatedExerciseSchema = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            response_model=ValidatedExerciseSchema,
            max_retries=7,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": build_exercise_prompt(module, slide_deck=slide_deck)}
            ]
        )
        
        print(f"  -> GENERATION & VERIFICATION SUCCESS: {exercise.title}")

        # JSON Metadata
        json_path = os.path.join(output_dir, f"{module.id}_generated.json")
        with open(json_path, "w") as f:
            json.dump(exercise.model_dump(), f, indent=2)

        # Starter Code (.py)
        exercise_path = os.path.join(output_dir, f"{module.id}_exercise.py")
        with open(exercise_path, "w") as f:
            f.write(f'"""\n{exercise.title}\n\nInstructions:\n{exercise.instructions}\n"""\n\n')
            f.write(clean_code_snippet(exercise.starter_code) + "\n")

        # Solution Code (.py)
        solution_path = os.path.join(output_dir, f"{module.id}_solution.py")
        with open(solution_path, "w") as f:
            f.write(f'"""\nSolution: {exercise.title}\n"""\n\n')
            f.write(clean_code_snippet(exercise.solution_code) + "\n")

        # Unit Test (.py)
        test_path = os.path.join(output_dir, f"{module.id}_test.py")
        with open(test_path, "w") as f:
            f.write(f'"""\nUnit Tests: {exercise.title}\n"""\n\n')
            f.write(clean_code_snippet(exercise.unit_test) + "\n")

        print(f"Saved all module assets to '{output_dir}/':")
        print(f"  - {slides_json_path}")
        print(f"  - {pptx_path}")
        print(f"  - {json_path}")
        print(f"  - {exercise_path}")
        print(f"  - {solution_path}")
        print(f"  - {test_path}")

if __name__ == "__main__":
    test_live_generation()
