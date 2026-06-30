"""
Authentication dependencies for FastAPI routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from ..db.session import get_db
from ..models.operator import Operator
from .security import decode_access_token

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Operator:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
    
    Returns:
        Current authenticated operator
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(Operator).filter(Operator.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Operator = Depends(get_current_user)
) -> Operator:
    """
    Dependency to get the current active user.
    Can be extended to check for account status (active/disabled).
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current active operator
    
    Raises:
        HTTPException: If user is inactive
    """
    # Add account status check here if needed
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


async def require_admin(
    current_user: Operator = Depends(get_current_active_user)
) -> Operator:
    """
    Dependency to require admin role.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current operator if admin
    
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_user_ws(
    token: str,
    db: Session = Depends(get_db)
) -> Operator:
    """
    Dependency to get the current authenticated user from JWT token for WebSocket.
    
    Args:
        token: JWT token string from query parameter
        db: Database session
    
    Returns:
        Current authenticated operator
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    # Decode token
    payload = decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(Operator).filter(Operator.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user
