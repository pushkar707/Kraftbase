from pydantic import BaseModel, EmailStr, Field

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)

class UserRegisteration(UserLogin):
    username: str = Field(min_length=5, max_length=50)