from tritonclient.grpc import InferenceServerClient
from app.utils.logger import logger
import time
from app.constants import TRITON_SERVER_URL, NEXUSRAVEN_MODEL_NAME

triton_client = InferenceServerClient(TRITON_SERVER_URL)

def query_raven(prompt: str) -> str:
    try:
        start_time = time.time()
        logger.info(f"Sending prompt to NexusRavenV2: {prompt}")
        response = triton_client.infer(NEXUSRAVEN_MODEL_NAME, prompt)
        raven_call = response.generated_text.replace("Call:", "").strip()
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"NexusRavenV2 execution time: {execution_time:.2f} seconds")
        return raven_call
    except Exception as e:
        logger.error(f"Error occurred while querying NexusRavenV2: {str(e)}")
        raise e

def prepare_raven_prompt(input: str, api_chunk: str) -> str:
    logger.info("Preparing prompt for NexusRavenV2")
    api_functions = api_chunk.strip().split('\n')
    prompt = ""
    for func in api_functions:
        prompt += f"Function Call:\n{func}\n\n"
    prompt += f"User Query: {input}"
    return prompt