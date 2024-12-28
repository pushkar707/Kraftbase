from pydantic import BaseModel
from typing import List, Union


class Response(BaseModel):
    field_id: int
    value: Union[str, int, bool]


class SubmitForm(BaseModel):
    response: List[Response]
