from schema.User import UserRegisteration, UserLogin
from models import User
import asyncio
from utils import hash_password, verify_password
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from db import db_dependency
from sqlalchemy import select


async def create_user(user: UserRegisteration, db: db_dependency):
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=await asyncio.to_thread(hash_password, user.password)
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        await db.rollback()
        if 'username' in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        elif "email" in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )


async def verify_user(user: UserLogin, db: db_dependency):
    db_user = (await db.execute(select(User).filter(User.email == user.email))).scalar_one_or_none()
    if not db_user:
        raise HTTPException(401, 'Invalid credentials')
    is_password_correct = await asyncio.to_thread(verify_password, user.password, db_user.hashed_password)
    if not is_password_correct:
        raise HTTPException(401, 'Invalid credentials')
    return db_user
