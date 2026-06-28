"""
Common dependencies for API routes.
"""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from ..db.session import get_db

# Type alias for database session dependency
DBSession = Annotated[Session, Depends(get_db)]
