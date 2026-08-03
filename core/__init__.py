from .ai_setup import get_instructor_client
from .context import (
    build_system_prompt,
    build_slide_prompt,
    build_exercise_prompt,
    build_qa_prompt,
    get_rag_context,
)
from .sandbox import run_in_sandbox, clean_code_snippet, strip_fake_local_imports
from .slide_builder import build_pptx_deck
from .telemetry import load_phase1_telemetry, formulate_problem_statement, ProblemStatementSchema
from .schemas import (
    Module,
    Slide,
    SlideDeckSchema,
    ExerciseSolutionSchema,
    UnitTestSchema,
    ValidatedExerciseSchema,
)

__all__ = [
    "get_instructor_client",
    "build_system_prompt",
    "build_slide_prompt",
    "build_exercise_prompt",
    "build_qa_prompt",
    "get_rag_context",
    "run_in_sandbox",
    "clean_code_snippet",
    "strip_fake_local_imports",
    "build_pptx_deck",
    "load_phase1_telemetry",
    "formulate_problem_statement",
    "ProblemStatementSchema",
    "Module",
    "Slide",
    "SlideDeckSchema",
    "ExerciseSolutionSchema",
    "UnitTestSchema",
    "ValidatedExerciseSchema",
]
