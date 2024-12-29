from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from fastapi import Depends
from typing import Annotated

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,

)
Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session
db_dependency = Annotated[Session, Depends(get_db)]
