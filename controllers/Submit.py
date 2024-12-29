from fastapi import Request, Query
from services.Form import get_form_by_id
from services.Submit import create_submission, validate_submission, get_paginated_form_submissions, get_submissions_total_count
from schema.Submit import SubmitForm
from db import db_dependency


async def submit_form_func(form_id: int, submission: SubmitForm, db: db_dependency, request: Request):
    form = await get_form_by_id(form_id, db, request)
    data = validate_submission(form, submission)
    await create_submission(data, form.id, db)
    return {'message': 'Submission added successfully', 'submission': {'responses': data}}


async def get_form_submissions_func(
        form_id: int,
        db: db_dependency,
        request: Request,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=50)
):
    form = await get_paginated_form_submissions(form_id, db, request, page, limit)
    total_count = await get_submissions_total_count(form_id, db)
    return {'total_count': total_count, 'page': page, 'limit': limit, 'submissions': form.submissions}
