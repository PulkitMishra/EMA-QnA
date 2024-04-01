from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.utils.database import Base

class UserFeedback(Base):
    __tablename__ = 'user_feedback'
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('user_queries.id'))
    feedback_text = Column(String)
    rating = Column(Integer)
    timestamp = Column(DateTime)