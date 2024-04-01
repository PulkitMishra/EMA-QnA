from kafka import KafkaProducer
from app.utils.logger import logger
import json
from app.constants import KAFKA_BOOTSTRAP_SERVERS

kafka_producer = None

def initialize_kafka_producer():
    global kafka_producer
    if not kafka_producer:
        logger.info("Initializing Kafka producer")
        kafka_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

def get_kafka_producer():
    if not kafka_producer:
        initialize_kafka_producer()
    return kafka_producer