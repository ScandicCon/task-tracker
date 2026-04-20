from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class CreateUser(SQLModel):
    username: str
    email: EmailStr
    password: str

class LoginUser(SQLModel):
    username: str
    password: str
    email: EmailStr = Field(default=None)