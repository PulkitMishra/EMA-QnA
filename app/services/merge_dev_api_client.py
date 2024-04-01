from fastapi import HTTPException
from typing import Dict, Any
from app.services.api_client import APIClient
from app.schemas.api_key import APIKey
from app.utils.logger import logger
import requests
import time

class MergeDevAPIClient(APIClient):
    def execute_api_call(self, call: str, api_key: APIKey, fallback: Callable[[str], Any] = None):
        start_time = time.time()
        logger.info(f"Executing Merge.dev API call: {call}")
        try:
            locals_dict = {'api_key': api_key}
            exec(call, globals(), locals_dict)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Merge.dev API call execution time: {execution_time:.2f} seconds")
            
            cleaned_response = self.validate_and_clean_data(locals_dict)
            return cleaned_response
        except NameError as e:
            if fallback:
                logger.warning(f"Missing parameter in API call: {str(e)}. Using fallback.")
                return fallback(str(e))
            else:
                logger.error(f"Missing parameter in API call: {str(e)}. No fallback provided.")
                raise HTTPException(status_code=400, detail=f"Missing parameter in API call: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Merge.dev API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Merge.dev API error: {str(e)}")
    
    @staticmethod
    def validate_and_clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement data validation and cleaning logic here
        # Example: Remove any null or invalid values
        cleaned_data = {k: v for k, v in data.items() if v is not None}
        return cleaned_data