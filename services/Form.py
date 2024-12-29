from fastapi import Request, HTTPException
from db import db_dependency
from models import Form
from schema.Form import CreateForm
from sqlalchemy import delete, select


async def create_form(form: CreateForm, request: Request, db: db_dependency):
    fields = [field.model_dump() for field in form.fields]
    db_form = Form(
        title=form.title,
        description=form.description,
        fields=fields,
        user_id=request.state.user['id']
    )
    db.add(db_form)
    await db.commit()
    await db.refresh(db_form)
    return db_form


async def delete_form(form_id: int, db: db_dependency, request: Request):
    await db.execute(delete(Form).filter(
        Form.id == form_id,
        Form.user_id == request.state.user['id']
    ))
    await db.commit()
    return form_id


async def get_all_forms(db: db_dependency, request: Request):
    return (await db.execute(select(Form).filter(
        Form.user_id == request.state.user['id']
    ))).scalars().all()


async def get_form_by_id(form_id: int, db: db_dependency, request: Request):
    form = (await db.execute(select(Form).filter(
        Form.id == form_id
    ))).scalar_one_or_none()
    if not form:
        raise HTTPException(404, 'Form not found')
    return form
