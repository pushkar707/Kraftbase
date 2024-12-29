from fastapi import FastAPI, Depends, Response, HTTPException, Request, Query
from starlette.middleware.base import BaseHTTPMiddleware
import models
from models import User, Form, Submission
from db import engine, SessionLocal
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import func
from typing import Annotated
from schema.User import UserRegisteration, UserLogin
from schema.Form import CreateForm
from schema.Submit import SubmitForm
from utils import verify_password, hash_password, redis_client, generate_session_id, get_simple_type
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
        url_path = request.url.path
        if any(url_path.startswith(path) for path in ['/forms']):
            if (not any(url_path.startswith(path) for path in ['/forms/submit'])):
                session_id = request.cookies.get('sid')
                user = redis_client.get(f'session:{session_id}')
                if not user:
                    raise HTTPException(
                        401, 'Please login to access this route')
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
    return {'message': 'Form deleted successfully', 'form_id': form_id}


@app.get('/forms')
def get_all_forms(db: db_dependency, request: Request):
    forms = db.query(Form).filter(
        Form.user_id == request.state.user['id']
    ).all()
    # with entitites field not working as fields is a JSON, hence need to explicitly remove user_id as a quicker solutuon
    forms_updated = [
        {'id': form.id, 'title': form.title,
            'description': form.description, 'fields': form.fields}
        for form in forms
    ]
    return {'message': 'Fetched all forms successfully', 'data': {'forms': forms_updated}}


@app.get('/forms/{form_id}')
def get_one_form(form_id: int, db: db_dependency, request: Request):
    form = db.query(Form).filter(
        Form.id == form_id,
        Form.user_id == request.state.user['id']
    ).first()
    if not form:
        raise HTTPException(404, 'Form not found')
    # with entitites field not working as fields is a JSON, hence need to explicitly remove user_id as a quicker solutuon
    form_updated = {
        'id': form.id,
        'title': form.title,
        'description': form.description,
        'fields': form.fields
    }
    return {'message': 'Fetched all forms successfully', 'data': {'form': form_updated}}


# FORM SUBMISSION
@app.post('/forms/submit/{form_id}')
def submit_form(form_id: int, submission: SubmitForm, db: db_dependency, request: Request):
    form = db.query(Form).filter(
        Form.id == form_id
    ).first()
    if not form:
        raise HTTPException(404, 'Form not found')

    data = {}

    for form_field in form.fields:
        curr_response_arr = [
            res for res in submission.response if res.field_id == form_field['field_id']
        ]
        if not curr_response_arr and form_field['required']:
            raise HTTPException(400, 'A required field is missing')
        if (curr_response_arr):
            curr_response = curr_response_arr[0]
            if form_field['type'] != get_simple_type(curr_response.value):
                raise HTTPException(
                    400, 'Response is not in valid format/type')
            data[curr_response.field_id] = curr_response.value

    if not data:
        raise HTTPException(
            400, 'You need to fill out atleast one item to submit a response')
    db_submission = Submission(data=data, form_id=form.id)
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return {'message': 'Submission added successfully', 'submission': {'responses': data}}


@app.post('/forms/submissions/{form_id}')
def get_form_submissions(
    form_id: int,
    db: db_dependency,
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)

):
    db_form = db.query(Form).options(
        joinedload(Form.submissions)
    ).filter(
        Form.id == form_id,
        Form.user_id == request.state.user['id']
    ).limit(limit).offset(
        (page - 1) * limit
    ).first()
    if not db_form:
        raise HTTPException(404, 'Form not found')

    total_count = db.query(func.count(Submission.submission_id)).filter(
        Submission.form_id == form_id).scalar()
    return {'total_count': total_count, 'page': page, 'limit': limit, 'submissions': db_form.submissions}
