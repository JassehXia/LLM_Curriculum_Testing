# Direct import
from schemas.module_types import Module
from schemas.generation_types import ValidatedExerciseSchema

# Or convenient top-level package import
from schemas import Module, ValidatedExerciseSchema, SlideDeckSchema

from typing import Dict, Any, Optional

def build_system_prompt() -> str:
    return (
        "You are an expert deep learning educator. "
        "Generate curriculum content following Bloom's Taxonomy and ABET outcomes. "
        "All generated PyTorch code must be clean, syntactically correct, and execute without errors."
    )

def build_exercise_prompt(module: Module, metrics: Optional[Dict[str, Any]] = None) -> str:
    prompt = (
        f"Generate a PyTorch exercise for module '{module.title}' (Week {module.week}).\n"
        f"Context: {module.context}\n"
        f"Difficulty: {module.difficulty}\n"
    )
    if metrics:
        prompt += f"\nPipeline Artifact Metrics:\n{metrics}\n"
    return prompt
