from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mobile = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    email = Column(String(120), unique=True, nullable=True, index=True)
    addresses = Column(Text, nullable=True, default="[]")  # JSON stored as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.mobile}>"
