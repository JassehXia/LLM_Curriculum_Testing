# Direct import
from schemas.module_types import Module
from schemas.generation_types import ValidatedExerciseSchema

# Or convenient top-level package import
from schemas import Module, ValidatedExerciseSchema, SlideDeckSchema

from typing import Dict, Any, Optional

def build_system_prompt() -> str:
    return (
        "You are an expert deep learning educator.\n"
        "Generate curriculum content following Bloom's Taxonomy and ABET outcomes.\n"
        "CRITICAL CODE RULES:\n"
        "1. Every `solution_code` and `unit_test` string MUST be a fully self-contained, valid Python script.\n"
        "2. ALWAYS include all necessary module imports at the very top of `solution_code` and `unit_test` (e.g., `import torch`, `import torch.nn as nn`, `import torch.nn.functional as F`).\n"
        "3. All generated PyTorch code must execute cleanly without SyntaxError, NameError, or AttributeError.\n"
        "4. In `unit_test`, test the classes/functions defined in `solution_code` directly in memory. NEVER use placeholder imports (e.g. `from your_module import ...`) or load non-existent files (`torch.load('path...')`).\n"
        "5. In `unit_test`, pass a dummy tensor (e.g., `torch.randn(1, 1, 64, 64)`) into the model and assert that the output tensor shape matches expectation.\n"
        "6. Keep model architectures lightweight (2-3 stages). Use `torch.cat([upsampled, skip], dim=1)` for skip connections with matching spatial height/width."
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
