from fastapi import APIRouter, Response, Request
from schema.User import UserRegisteration, UserLogin
from db import db_dependency
from controllers.User import register_func, login_func, logout_func

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register')
async def register(user: UserRegisteration, db: db_dependency, response: Response):
    return await register_func(user, db, response)


@router.post('/login')
async def login(user: UserLogin, db: db_dependency, response: Response):
    return await login_func(user, db, response)


@router.post('/logout')
async def logout(request: Request, response: Response):
    return await logout_func(request, response)
