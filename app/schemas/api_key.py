from pydantic import BaseModel
from typing import Dict

class APIKey(BaseModel):
    merge_api_key: str
    linked_account_tokens: Dict[str, str]