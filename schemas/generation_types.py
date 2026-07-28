from pydantic import BaseModel, Field
from typing import List, Optional

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
