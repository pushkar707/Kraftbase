from fastapi import APIRouter, Request
from db import db_dependency
import routes.Submit
from schema.Form import CreateForm
from controllers.Form import create_form_func, delete_form_func, get_all_forms_func, get_one_form_func
import routes

router = APIRouter(prefix='/forms', tags=['Forms'])
router.include_router(router=routes.Submit.router)


@router.post('/create')
async def create_form(form: CreateForm, request: Request, db: db_dependency):
    return await create_form_func(form, request, db)


@router.delete('/delete/{form_id}')
async def delete_form(form_id: int, db: db_dependency, request: Request):
    return await delete_form_func(form_id, db, request)


@router.get('/')
async def get_all_forms(db: db_dependency, request: Request):
    """
    List all forms created by the current user
    """
    return await get_all_forms_func(db, request)


@router.get('/{form_id}')
async def get_one_form(form_id: int, db: db_dependency, request: Request):
    return await get_one_form_func(form_id, db, request)
