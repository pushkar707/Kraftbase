from models import User
from sqlalchemy import select
import pytest
from services.User import create_user
from schema.User import UserRegisteration

# TODO: Check that key is added to redis
# Further, various tests can be written like checking for 422 error. Nnot focusing on coverage due to time constraints


@pytest.mark.asyncio
async def test_register_user(client, db):
    email = 'user@mail.com'
    username = 'username'
    response = await client.post(
        "/auth/register", json={'username': username, 'email': email, 'password': 'password'}
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"

    assert response.cookies.get('sid') is not None

    db_user = (await db.execute(select(User).filter(User.email == email))).scalar_one_or_none()
    assert db_user is not None
    assert db_user.username == username


@pytest.mark.asyncio
async def test_login_user_correct_creds(client, db):
    email = 'base@mail.com'
    password = 'password'
    await create_user(UserRegisteration(
        email=email,
        password=password,
        username='anything'
    ), db)
    response = await client.post(
        "/auth/login", json={'email': email, 'password': password}
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json()["message"] == 'Logged in successfully'
    assert response.cookies.get('sid') is not None


@pytest.mark.asyncio
async def test_login_user_incorrect_creds(client):
    email = 'user@mail.com'
    response = await client.post(
        "/auth/login", json={'email': email, 'password': 'password_wrong'}
    )
    print(response.json())
    assert response.status_code == 401
    assert response.json()["detail"] == 'Invalid credentials'


@pytest.mark.asyncio
async def test_logout(client, db):
    # Logging in the user first
    email = 'base@mail.com'
    password = 'password'
    await create_user(UserRegisteration(
        email=email,
        password=password,
        username='anything'
    ), db)
    await client.post(
        "/auth/login", json={'email': email, 'password': password}
    )

    # Testing logout
    response = await client.post(
        "/auth/logout"
    )
    assert response.cookies.get('sid') is None
