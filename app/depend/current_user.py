from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserOperations
from app.security.jwt import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user_ops = UserOperations(db)
    user = user_ops.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

def required_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

def required_organization(current_user=Depends(get_current_user)):
    if current_user.role != "organization":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization privileges required")
    return current_user

def required_user(current_user=Depends(get_current_user)):
    if current_user.role != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User privileges required")
    return current_user

def required_user_or_organization(current_user=Depends(get_current_user)):
    if current_user.role not in ("user", "organization"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User or organization privileges required")
    return current_user

def required_user_or_admin(current_user=Depends(get_current_user)):
    if current_user.role not in ("user", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User or admin privileges required")
    return current_user

def required_organization_or_admin(current_user=Depends(get_current_user)):
    if current_user.role not in ("organization", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization or admin privileges required")
    return current_user
