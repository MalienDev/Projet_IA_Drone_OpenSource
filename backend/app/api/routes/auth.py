"""
Authentication routes for login, token management, and user operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..schemas import LoginRequest, TokenResponse, PasswordChangeRequest
from ...db.session import get_db
from ...models.operator import Operator
from ...auth.security import verify_password, get_password_hash, create_access_token
from ...auth.dependencies import get_current_active_user, require_admin

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    """
    # Find user by username
    user = db.query(Operator).filter(Operator.username == login_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        username=user.username,
        role=user.role
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Operator = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: Operator = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    """
    return {
        "username": current_user.username,
        "role": current_user.role,
        "created_at": current_user.created_at
    }


@router.post("/create-operator")
async def create_operator(
    username: str,
    password: str,
    role: str = "operator",
    current_user: Operator = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new operator (admin only).
    """
    # Check if user already exists
    existing = db.query(Operator).filter(Operator.username == username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create new operator
    new_operator = Operator(
        username=username,
        password_hash=get_password_hash(password),
        role=role
    )
    db.add(new_operator)
    db.commit()
    
    return {
        "message": "Operator created successfully",
        "username": username,
        "role": role
    }
