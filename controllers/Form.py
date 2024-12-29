from fastapi import Request
from db import db_dependency
from schema.Form import CreateForm
from services.Form import create_form, delete_form, get_all_forms, get_form_by_id


async def create_form_func(form: CreateForm, request: Request, db: db_dependency):
    form = await create_form(form, request, db)
    return {'message': 'Form created successfully', 'data': {
        'form': form
    }}


async def delete_form_func(form_id: int, db: db_dependency, request: Request):
    await delete_form(form_id, db, request)
    return {'message': 'Form deleted successfully', 'form_id': form_id}


async def get_all_forms_func(db: db_dependency, request: Request):
    forms = await get_all_forms(db, request)
    # with entitites field not working as fields is a JSON, hence need to explicitly remove user_id as a quicker solutuon
    forms_updated = [
        {'id': form.id, 'title': form.title,
            'description': form.description, 'fields': form.fields}
        for form in forms
    ]
    return {'message': 'Fetched all forms successfully', 'data': {'forms': forms_updated}}


async def get_one_form_func(form_id: int, db: db_dependency, request: Request):
    form = await get_form_by_id(form_id, db, request)
    # with entitites field not working as fields is a JSON, hence need to explicitly remove user_id as a quicker solutuon
    form_updated = {
        'id': form.id,
        'title': form.title,
        'description': form.description,
        'fields': form.fields
    }
    return {'message': 'Fetched form successfully', 'data': {'form': form_updated}}
