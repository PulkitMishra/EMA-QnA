from fastapi import FastAPI
from app.routers.query_router import router as query_router
from app.utils.database import Base, engine
from app.services.kafka_service import consume_from_kafka, consume_user_feedback_from_kafka
import threading

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(query_router)

@app.on_event("startup")
def startup_event():
    threading.Thread(target=consume_from_kafka).start()
    threading.Thread(target=consume_user_feedback_from_kafka).start()