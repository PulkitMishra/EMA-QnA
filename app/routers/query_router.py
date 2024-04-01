from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from app.schemas.api_key import APIKey
from app.dependencies import get_api_key
from app.services.merge_dev_api_client import MergeDevAPIClient
from app.services.nexus_raven_service import query_raven, prepare_raven_prompt
from app.services.anthropic_service import query_claude
from app.services.kafka_producer import get_kafka_producer
from app.utils.logger import logger
import json
import time

router = APIRouter()

def load_api_refs_from_db() -> List[Dict[str, Any]]:
    logger.info("Loading API references from database")
    with open('api_refs.json') as f:
        return json.load(f)

def get_api_chunks(api_refs: List[Dict[str, Any]], chunk_size: int = 5000) -> List[str]:
    logger.info(f"Splitting API references into chunks of size {chunk_size}")
    chunks = []
    current_chunk = ""

    for ref in api_refs:
        ref_str = json.dumps(ref)
        if len(current_chunk) + len(ref_str) > chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += ref_str + "\n"

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

@router.post("/query")
def handle_query(input: str, api_key: APIKey = Depends(get_api_key), api_client: MergeDevAPIClient = Depends(MergeDevAPIClient)):
    try:
        start_time = time.time()
        logger.info(f"Received user query: {input}")

        # Load API references from the database
        api_refs = load_api_refs_from_db()

        # Get API reference chunks
        api_chunks = get_api_chunks(api_refs)
        logger.info(f"Retrieved {len(api_chunks)} API reference chunks")

        # Query NexusRavenV2 for each chunk and execute the returned function call
        api_responses = {}
        for chunk in api_chunks:
            raven_prompt = prepare_raven_prompt(input, chunk)
            raven_call = query_raven(raven_prompt)
            logger.info(f"NexusRavenV2 generated function call: {raven_call}")
            
            retry_count = 0
            while retry_count < 3:
                try:
                    def fallback_handler(error_message: str) -> Dict[str, Any]:
                        # Implement fallback logic here
                        # Example: Provide a generic response or request clarification from the user
                        return {
                            "fallback_response": f"Missing parameter: {error_message}. Please provide the necessary information."
                        }

                    api_response = api_client.execute_api_call(raven_call, api_key, fallback=fallback_handler)
                    logger.info(f"Executed API call: {raven_call}")
                    api_responses.update(api_response)
                    break
                except HTTPException as e:
                    if e.status_code == 429:
                        retry_count += 1
                        wait_time = 2 ** retry_count
                        logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        raise e

        # Circuit breaker pattern
        try:
            claude_response = query_claude(input, api_responses)
        except Exception as e:
            logger.error(f"Error querying Claude: {str(e)}")
            # Fallback to a default response
            claude_response = "Apologies, I am currently unable to provide a response. Please try again later."
        logger.info(f"Generated natural language response: {claude_response}")

        interaction = {
            'user_input': input,
            'raven_output': raven_call,
            'api_responses': api_responses,
            'final_output': claude_response
        }
        kafka_producer = get_kafka_producer()
        kafka_producer.send('interactions', interaction)
        logger.info(f"Sent interaction details to Kafka")

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Query execution time: {execution_time:.2f} seconds")

        return claude_response

    except Exception as e:
        logger.error(f"An error occurred while processing the query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")