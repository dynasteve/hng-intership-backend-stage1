from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from datetime import datetime
from app.database import Base

class StringModel(Base):
    __tablename__ = "strings"

    id = Column(String, primary_key=True, index=True)  # sha256 hash
    value = Column(String, unique=True, nullable=False)
    length = Column(Integer, nullable=False)
    is_palindrome = Column(Boolean, nullable=False)
    unique_characters = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    character_frequency_map = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
