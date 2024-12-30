from models import User
from sqlalchemy import select
import pytest

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
