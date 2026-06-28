"""
Operator model.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from ..db.base import Base


class Operator(Base):
    """Operator model representing system operators."""
    
    __tablename__ = "operators"
    
    username = Column(String, primary_key=True, index=True)
    password_hash = Column(String, nullable=False)  # Hashed password
    role = Column(String, default="operator")  # "operator", "admin"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Operator(username={self.username}, role={self.role})>"
