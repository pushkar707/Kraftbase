from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = 'postgresql+asyncpg://postgres:postgres@localhost:5432/kraftbase_assignment'
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,

)
Base = declarative_base()
