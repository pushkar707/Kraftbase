from fastapi import FastAPI, Request, Query
import models
from db import engine, db_dependency
from middleware.AuthMiddleware import AuthMiddleware
from controllers.Submit import get_form_submissions_func
import routes
import routes.Form
import routes.User

app = FastAPI()


@app.on_event("startup")
async def main():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


app.add_middleware(AuthMiddleware)
app.include_router(router=routes.User.router)
app.include_router(router=routes.Form.router)


@app.post('/forms/submissions/{form_id}')
async def get_form_submissions(
    form_id: int,
    db: db_dependency,
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    return await get_form_submissions_func(form_id, db, request, page, limit)
