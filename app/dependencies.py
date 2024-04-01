from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.api_key import APIKey

security = HTTPBearer()

def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # TODO: Implement secure API key retrieval and validation
    return APIKey(merge_api_key="dummy_key", linked_account_tokens={})