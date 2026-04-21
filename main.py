from sqlmodel import SQLModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.db.session import engine 
from app.model.user import User
from app.model.task import Task

from app.api.auth import router as auth_routers
from app.api.users import router as user_routers
from app.api.task import router as task_routers

app = FastAPI()
app.include_router(auth_routers)
app.include_router(user_routers)
app.include_router(task_routers)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def home():
    return FileResponse("index.html")