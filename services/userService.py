from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from typing import Optional, Union
from settings import ALGORITHM, AUTH_SECRET
import uuid
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update

from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from database.session import get_async_session
from services import bcryptService
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(token, AUTH_SECRET, algorithms=[ALGORITHM], options={"verify_exp": True})
        print(f"jwt payload: {payload}")
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid token")
        user_id = int(user_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        print(f"the error is; {e}")
        raise HTTPException(status_code=403, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=403, detail= f"Error occurred with token validation : {e}")

    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User not accessible")
    return user

        
async def check_password(user: User, password: str) -> bool:
    return await bcryptService.check_password(password=password, encrypted=user.password)

async def update_password(session: AsyncSession, user:User, raw_password):
    user.password = await bcryptService.make_password(raw_password)
    session.add(user)
    await session.commit()
    return user
    
async def get_user_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where (User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user

async def create_user(session: AsyncSession, email: str, raw_password: str) -> Optional[User]:
    existing_stmt = select(User).where(User.email == email)
    result = await session.execute(existing_stmt)
    if result.scalar_one_or_none():
        return None
    
    encrypted_password = await bcryptService.make_password(password_string=raw_password)
    user = User(email=email, password=encrypted_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user
