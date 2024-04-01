import anthropic
from app.utils.logger import logger
import time
import json
from app.constants import ANTHROPIC_MODEL_NAME

anthropic_client = anthropic.Anthropic()

def query_claude(input: str, api_responses: Dict[str, Any]) -> str:
    try:
        start_time = time.time()
        logger.info("Querying Claude for natural language response")
        messages = [
            {"role": "user", "content": input},
            {"role": "system", "content": "API Responses:\n" +
                                        "\n".join([f"{k}: {json.dumps(v)}" for k, v in api_responses.items()])}
        ]
        claude_response = anthropic_client.messages.create(
            model=ANTHROPIC_MODEL_NAME,
            max_tokens=1024,
            messages=messages
        )
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Claude execution time: {execution_time:.2f} seconds")
        return claude_response.content[0].text
    except Exception as e:
        logger.error(f"Error occurred while querying Claude: {str(e)}")
        raise e