from pydantic import BaseModel
from typing import Dict, Any

class Interaction(BaseModel):
    user_input: str
    raven_output: str
    api_responses: Dict[str, Any]
    final_output: str