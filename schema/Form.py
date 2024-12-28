from pydantic import BaseModel
from typing import Literal, List


class FieldType(BaseModel):
    field_id: int
    type: Literal['string', 'number', 'boolean']
    label: str
    required: bool


class CreateForm(BaseModel):
    title: str
    description: str
    fields: List[FieldType]
