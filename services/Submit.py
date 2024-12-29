from db import db_dependency
from models import Submission, Form
from fastapi import HTTPException, Request, Query
from schema.Submit import SubmitForm
from utils import get_simple_type
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


def validate_submission(form: Form, submission: SubmitForm):
    """
    Checks:
    1) if any required field is missing
    2) datatype of values match with type of field
    """

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
    return data


async def create_submission(data, form_id: int, db: db_dependency):
    db_submission = Submission(data=data, form_id=form_id)
    db.add(db_submission)
    await db.commit()
    await db.refresh(db_submission)
    return db_submission


async def get_paginated_form_submissions(
    form_id: int,
    db: db_dependency,
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    db_form = (await db.execute(select(Form).options(
        joinedload(Form.submissions)
    ).filter(
        Form.id == form_id,
        Form.user_id == request.state.user['id']
    ).limit(limit).offset(
        (page - 1) * limit
    ))).scalars().unique().first()
    if not db_form:
        raise HTTPException(404, 'Form not found')
    return db_form


async def get_submissions_total_count(form_id: int, db: db_dependency):
    return (await db.execute(select(func.count(Submission.submission_id)).filter(
        Submission.form_id == form_id))).scalar()
