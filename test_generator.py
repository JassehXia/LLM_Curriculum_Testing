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
        model="Qwen/Qwen2.5-3B-Instruct",
        response_model=ValidatedExerciseSchema,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_exercise_prompt(module)}
        ]
    )
    
    print("\n========== GENERATION SUCCESS ==========")
    print(f"Title: {exercise.title}")
    print(f"Instructions:\n{exercise.instructions}")
    print(f"Starter Code:\n{exercise.starter_code}")

    # 4. Save validated output object to outputs/ directory
    import os, json
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{module.id}_generated.json")
    with open(output_file, "w") as f:
        json.dump(exercise.model_dump(), f, indent=2)
    print(f"\nSaved generated exercise to: {output_file}")

if __name__ == "__main__":
    test_live_generation()
