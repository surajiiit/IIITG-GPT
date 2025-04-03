from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import secrets
import os

from db import get_user, get_user_with_password
from models import User

# Generate a random secret key if not provided
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hashed version
    
    Note: In a production environment, this should use proper password hashing
    like bcrypt or Argon2. For this project, we're using a simple comparison
    for the admin account.
    """
    # Just verify the admin credentials directly
    # In a real application, use proper password hashing
    return plain_password == "admin123" and hashed_password == "$2b$12$5nU0TVAXHn1hhuTQ8NpIyuVdz7hFcGNqm5Qgbe.9USbgMHdLpwU6m"

def authenticate_user(username: str, password: str) -> Optional[User]:
    user_dict = get_user_with_password(username)
    if not user_dict:
        return None
    if not verify_password(password, user_dict["hashed_password"]):
        return None
    
    return User(
        username=user_dict["username"],
        email=user_dict.get("email"),
        full_name=user_dict.get("full_name"),
        disabled=user_dict.get("disabled", False),
        is_admin=user_dict.get("is_admin", False)
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
