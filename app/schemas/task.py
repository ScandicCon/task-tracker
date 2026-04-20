from sqlmodel import SQLModel
from typing import Optional

class CreateTask(SQLModel):
    name: str
    description: Optional[str] = None