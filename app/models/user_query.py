from sqlalchemy import Column, Integer, String, DateTime
from app.utils.database import Base

class UserQuery(Base):
    __tablename__ = 'user_queries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    query_text = Column(String)
    timestamp = Column(DateTime)