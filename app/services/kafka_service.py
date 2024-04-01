from kafka import KafkaConsumer
from app.models.user_query import UserQuery
from app.models.intermediate_output import IntermediateOutput
from app.models.api_response import APIResponse
from app.models.final_output import FinalOutput
from app.models.user_feedback import UserFeedback
from app.schemas.interaction import Interaction
from app.utils.database import SessionLocal
from app.utils.logger import logger
from typing import Dict, Any
import json
from datetime import datetime
from pydantic import ValidationError
from app.constants import KAFKA_BOOTSTRAP_SERVERS

kafka_consumer = KafkaConsumer(
    'interactions',
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

def store_interaction(interaction_data: Dict[str, Any]) -> None:
    try:
        logger.info("Validating interaction data")
        interaction = Interaction(**interaction_data)

        logger.info("Storing interaction in the database")
        session = SessionLocal()
        try:
            user_query = UserQuery(user_id=1, query_text=interaction.user_input, timestamp=datetime.now())
            session.add(user_query)
            session.flush()

            intermediate_output = IntermediateOutput(query_id=user_query.id, output_data=interaction.raven_output, timestamp=datetime.now())
            session.add(intermediate_output)

            for api_name, response_data in interaction.api_responses.items():
                api_response = APIResponse(query_id=user_query.id, api_name=api_name, response_data=json.dumps(response_data), timestamp=datetime.now())
                session.add(api_response)

            final_output = FinalOutput(query_id=user_query.id, output_text=interaction.final_output, timestamp=datetime.now())
            session.add(final_output)

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing interaction in the database: {str(e)}")
            raise e
        finally:
            session.close()
    except ValidationError as e:
        logger.error(f"Validation error for interaction data: {str(e)}")

def store_user_feedback(feedback: Dict[str, Any]) -> None:
    logger.info("Validating user feedback data")
    try:
        query_id = feedback['query_id']
        feedback_text = feedback['feedback_text']
        rating = feedback['rating']

        if not isinstance(query_id, int) or not isinstance(feedback_text, str) or not isinstance(rating, int):
            raise ValueError("Invalid data types for user feedback fields")

        logger.info("Storing user feedback in the database")
        session = SessionLocal()
        try:
            user_feedback = UserFeedback(query_id=feedback['query_id'], feedback_text=feedback['feedback_text'], rating=feedback['rating'], timestamp=datetime.now())
            session.add(user_feedback)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing user feedback in the database: {str(e)}")
            raise e
        finally:
            session.close()
    except (KeyError, ValueError) as e:
        logger.error(f"Validation error for user feedback data: {str(e)}")

def consume_from_kafka() -> None:
    logger.info("Starting Kafka consumer for interactions")
    for message in kafka_consumer:
        interaction = message.value
        store_interaction(interaction)
        logger.info(f"Stored interaction in the database: {interaction}")

def consume_user_feedback_from_kafka() -> None:
    logger.info("Starting Kafka consumer for user feedback")
    for message in kafka_consumer:
        feedback = message.value
        store_user_feedback(feedback)
        logger.info(f"Stored user feedback in the database: {feedback}")