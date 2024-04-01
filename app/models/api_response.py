from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.utils.database import Base

class APIResponse(Base):
    __tablename__ = 'api_responses'
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('user_queries.id'))
    api_name = Column(String)
    response_data = Column(String)
    timestamp = Column(DateTime)