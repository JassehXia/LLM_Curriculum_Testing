import yaml
from schemas import Module, ValidatedExerciseSchema, SlideDeckSchema
from context import build_system_prompt, build_exercise_prompt
from ai_setup import get_instructor_client

def test_live_generation():
    # 1. Ingest test.yaml config
    with open("test.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    module_data = config["curriculum"]["modules"][0]
    module = Module(**module_data)
    
    # 2. Get Instructor Client
    client = get_instructor_client(base_url="http://localhost:8000/v1")
    
    # 3. Request Structured Exercise Generation from Qwen
    print(f"Requesting exercise generation for: {module.title}...")
    exercise: ValidatedExerciseSchema = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        response_model=ValidatedExerciseSchema,
        max_retries=5,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_exercise_prompt(module)}
        ]
    )
    
    print("\n========== GENERATION SUCCESS ==========")
    print(f"Title: {exercise.title}")
    print(f"Instructions:\n{exercise.instructions}")
    print(f"Starter Code:\n{exercise.starter_code}")

    # 4. Save output assets to outputs/ directory
    import os, json
    from sandbox import clean_code_snippet

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # JSON Metadata
    json_path = os.path.join(output_dir, f"{module.id}_generated.json")
    with open(json_path, "w") as f:
        json.dump(exercise.model_dump(), f, indent=2)

    # Practice / Starter Code (.py)
    exercise_path = os.path.join(output_dir, f"{module.id}_exercise.py")
    with open(exercise_path, "w") as f:
        f.write(f'"""\n{exercise.title}\n\nInstructions:\n{exercise.instructions}\n"""\n\n')
        f.write(clean_code_snippet(exercise.starter_code) + "\n")

    # Reference Solution (.py)
    solution_path = os.path.join(output_dir, f"{module.id}_solution.py")
    with open(solution_path, "w") as f:
        f.write(f'"""\nSolution: {exercise.title}\n"""\n\n')
        f.write(clean_code_snippet(exercise.solution_code) + "\n")

    # Standalone Unit Test (.py)
    test_path = os.path.join(output_dir, f"{module.id}_test.py")
    with open(test_path, "w") as f:
        f.write(f'"""\nUnit Tests: {exercise.title}\n"""\n\n')
        f.write(clean_code_snippet(exercise.unit_test) + "\n")

    print(f"\nSaved generated output assets to '{output_dir}/':")
    print(f"  - {json_path}")
    print(f"  - {exercise_path}")
    print(f"  - {solution_path}")
    print(f"  - {test_path}")

if __name__ == "__main__":
    test_live_generation()
