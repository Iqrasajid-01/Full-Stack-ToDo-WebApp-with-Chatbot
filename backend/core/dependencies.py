from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session
from core.security import verify_token
from db.session import get_session
from typing import Dict, Optional


def get_token_from_header(request: Request):
    """
    Extract the JWT token from the Authorization header.
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    return token


def get_current_user(token: str = Depends(get_token_from_header)):
    """
    Get the current user from the JWT token in the Authorization header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Ensure user_id is returned as a string to match the database schema
    return str(user_id)