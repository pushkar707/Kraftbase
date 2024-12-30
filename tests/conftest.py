import pytest_asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from db import get_db, Base
from main import app
from httpx import AsyncClient, ASGITransport
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.environ.get('TEST_DB')

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

# AsyncSession for SQLAlchemy
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Fixture to create and drop tables in the test database


# @pytest_asyncio.fixture(scope="session", autouse=True)
# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield

# Fixture to provide a session to interact with the database during tests


@pytest_asyncio.fixture(scope="function")
async def db():
    async with TestingSessionLocal() as session:
        yield session  # Provide the session to the tests

# Fixture for overriding the `get_db` dependency


@pytest_asyncio.fixture(scope="function")
async def client(db):
    async def override_get_db():
        try:
            yield db
        finally:
            await db.close()  # Close the async session

    app.dependency_overrides[get_db] = override_get_db
    # FastAPI client for testing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client