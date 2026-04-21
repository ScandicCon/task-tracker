from sqlmodel import SQLModel, Field
from typing import Optional

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = Field(default=None)
    status: str = Field(default="free")
    user_id: Optional[int] = Field(default=None , foreign_key="user.id")