import instructor
from openai import OpenAI

def get_instructor_client(base_url: str="http://localhost:8000/v1") -> instructor.Instructor:
    """ Configures Instructor client targetting the vLLM endpoint"""
    raw_client = OpenAI(
        base_url = base_url,
        api_key="none"
    )

    return instructor.from_openai(raw_client, mode=instructor.Mode.JSON)