"""
Database session management.
"""

from typing import Generator
from sqlalchemy.orm import Session
from .base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
