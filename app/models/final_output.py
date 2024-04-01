from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.utils.database import Base

class FinalOutput(Base):
    __tablename__ = 'final_outputs'
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('user_queries.id'))
    output_text = Column(String)
    timestamp = Column(DateTime)