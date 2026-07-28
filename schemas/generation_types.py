from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from sandbox import run_in_sandbox

class Slide(BaseModel):
    title: str = Field(description="Title of the slide")
    bullet_points: List[str] = Field(description="3 to 4 concise bullet points explaining key concepts")
    code_snippet: Optional[str] = Field(None, description="Optional PyTorch snippet for code demonstration")

class SlideDeckSchema(BaseModel):
    deck_title: str = Field(description="Main topic or title of presentation")
    slides: List[Slide] = Field(description="List of presentation slides")

class ValidatedExerciseSchema(BaseModel):
    title: str = Field(description="Title of the coding exercise")
    instructions: str = Field(description="Problem statement and student directives")
    starter_code: str = Field(description="Starter PyTorch skeleton code containing TODO comments")
    solution_code: str = Field(description="Complete, fully working PyTorch reference solution code")
    unit_test: str = Field(description="Standalone PyTorch unit tests with asserts to verify solution_code")

    @model_validator(mode="after")
    def validate_solution_with_unit_tests(self):
        """Runs solution code against unit test in a subprocess"""
        success, log = run_in_sandbox(self.solution_code, self.unit_test)
        if not success:
            raise ValueError(
                f"Generated solution failed unit test verification in sandbox.\n"
                f"Execution log:\n{log}\n"
                f"Please fix the implementation errors in solution_code or unit_test."
            )
        return self