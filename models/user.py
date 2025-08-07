from sqlalchemy import Column, String, DateTime, Boolean, INTEGER
from sqlalchemy.orm import relationship
from models.base import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True, autoincrement= True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100))
    created_at = Column(DateTime(timezone= True), default= lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone= True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
