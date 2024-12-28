from fastapi import FastAPI, Depends, Response, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
import models
from models import User, Form
from db import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from schema.User import UserRegisteration, UserLogin
from schema.Form import CreateForm
from utils import verify_password, hash_password, redis_client, generate_session_id
from sqlalchemy.exc import IntegrityError
import json

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
SESSION_TIME = 60 * 60 * 24


@app.post('/auth/register')
def register(user: UserRegisteration, db: db_dependency, response: Response):
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hash_password(user.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback()
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

    session_id = generate_session_id()
    redis_client.setex(
        name=f'session:{session_id}',
        time=SESSION_TIME,
        value=json.dumps({'email': user.email, 'id': db_user.id})
    )
    response.set_cookie('sid', session_id, max_age=SESSION_TIME)
    return {'message': 'User registered successfully'}


@app.post('/auth/login')
def login(user: UserLogin, db: db_dependency, response: Response):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(401, 'Invalid credentials')
    is_password_correct = verify_password(
        user.password, db_user.hashed_password)
    if not is_password_correct:
        raise HTTPException(401, 'Invalid credentials')
    session_id = generate_session_id()
    redis_client.setex(
        name=f'session:{session_id}',
        time=SESSION_TIME,
        value=json.dumps({'email': user.email, 'id': db_user.id})
    )
    response.set_cookie('sid', session_id, max_age=SESSION_TIME)
    return {'message': 'Logged in successfully'}


@app.post('/auth/logout')
def logout(request: Request, response: Response):
    session_id = request.cookies.get('sid')
    response.delete_cookie('sid')
    redis_client.delete(f'session:{session_id}')
    return {'message': 'Logged out successfully'}


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if any(request.url.path.startswith(path) for path in ['/forms']):
            session_id = request.cookies.get('sid')
            user = redis_client.get(f'session:{session_id}')
            if not user:
                raise HTTPException(401, 'Please login to access this route')
            request.state.user = json.loads(user)
        return await call_next(request)


app.add_middleware(AuthenticationMiddleware)


@app.post('/forms/create')
def create_form(form: CreateForm, db: db_dependency, request: Request):
    fields = [field.model_dump() for field in form.fields]
    db_form = Form(
        title=form.title,
        description=form.description,
        fields=fields,
        user_id=request.state.user['id']
    )
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    return {'message': 'Form created successfully', 'data': {
        'form': db_form
    }}


@app.delete('/forms/delete/{form_id}')
def delete_form(form_id: int, db: db_dependency, request: Request):
    db.query(Form).filter(
        Form.id == form_id,
        Form.user_id == request.state.user['id']
    ).delete()
    db.commit()
    return {'message': 'Form deleted successfully'}
