from fastapi import APIRouter, Request
from controllers.Submit import submit_form_func
from db import db_dependency
from schema.Submit import SubmitForm

router = APIRouter(prefix='/submit', tags=['Form Submissions'])


@router.post('/{form_id}')
async def submit_form(form_id: int, submission: SubmitForm, db: db_dependency, request: Request):
    return await submit_form_func(form_id, submission, db, request)
