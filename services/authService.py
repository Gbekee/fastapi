from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from datetime import datetime, timezone
from jose import JWTError, jwt
from typing import Optional
import settings

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.AUTH_SECRET, algorithm=settings.ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, settings.AUTH_SECRET, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
    
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def create_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_URL_TTL_IN_SECONDS/60)
    payload = {"sub": email, "exp": expire, "scope": "reset_password"}
    return jwt.encode(payload, settings.AUTH_SECRET, algorithm= settings.ALGORITHM)

def decode_reset_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.AUTH_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("scope") != "reset_password":
            return None
        return payload.get("sub")  # email
    except JWTError:
        return None
