from services.User import create_user, verify_user
from utils import generate_session_id
from config import SESSION_TIME
import json
from schema.User import UserRegisteration, UserLogin
from redis_client import add_redis_session_key, delete_redis_key
from db import db_dependency
from fastapi import Response


async def register_func(user: UserRegisteration, db: db_dependency, response: Response):
    user = await create_user(user, db)
    session_id = await generate_session_id()
    await add_redis_session_key(session_id, user)
    response.set_cookie('sid', session_id, max_age=SESSION_TIME)
    return {'message': 'User registered successfully'}


async def login_func(user: UserLogin, db: db_dependency, response: Response):
    user = await verify_user(user, db)
    session_id = await generate_session_id()
    await add_redis_session_key(session_id, user)
    response.set_cookie('sid', session_id, max_age=SESSION_TIME)
    return {'message': 'Logged in successfully'}


async def logout_func(request, response):
    session_id = request.cookies.get('sid')
    response.delete_cookie('sid')
    await delete_redis_key(f'session:{session_id}')
    return {'message': 'Logged out successfully'}
