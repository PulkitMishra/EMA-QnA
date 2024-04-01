from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.utils.database import Base

class IntermediateOutput(Base):
    __tablename__ = 'intermediate_outputs'
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('user_queries.id'))
    output_data = Column(String)
    timestamp = Column(DateTime)