from datetime import timedelta, timezone, datetime
import jwt
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlmodel import select, Session
from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE, ALGORITHM 
from app.db.session import get_session
from app.model.user import User
from app.model.task import Task

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")
 
password_hasher = PasswordHash.recommended()

DUMMY_HASH  = password_hasher.hash("DUMMY_PASSWORD")

def password_hash(password: str):
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hasher.verify(plain_password, hashed_password)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token:str = Depends(oauth2_schema), session : Session = Depends(get_session)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    user = session.exec(select(User).where(user_id == User.id)).first()
    if not user:
        return HTTPException(status_code=401)
    return user


def get_task_by_id(
    task_id: int,
    session: Session = Depends(get_session)
):
    task = session.exec(
        select(Task).where(Task.id == task_id)).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
def require_status(allowed_statuses: list):
    def check_status(task: Task = Depends(get_task_by_id)):
        if task.status in allowed_statuses:
            return task
        else:
            raise HTTPException(status_code=400, detail="Invalid task status")
    return check_status


def require_in_progress_owner(
    task: Task = Depends(get_task_by_id),
    user: User = Depends(get_current_user)
):
    if task.status != "in progress":
        raise HTTPException(
            status_code=400,
            detail="Task is not in progress"
        )

    if task.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="This is not your task"
        )

    return task