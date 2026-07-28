from pydantic import BaseModel

class Module(BaseModel):
    id: str
    title: str
    week: int
    context: str
    difficulty: str