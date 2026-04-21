from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from datetime import timedelta, datetime, timezone

from app.schemas.task import CreateTask
from app.db.session import get_session
from app.core.security import require_in_progress_owner, get_task_by_id, get_current_user

from app.model.task import Task
from app.model.user import User



router = APIRouter(prefix="/tasks", tags=["Task"])


@router.post("/create")
def create_task(task: CreateTask, session:Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401 , detail="Неавторизованный пользователь")
    new_task = Task(
        name=task.name,
        description=task.description
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task

@router.patch("/{task_id}/take")
def take_task(
    task : Task = Depends (get_task_by_id),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    if task.status != "free":
        raise HTTPException(
        status_code=400,
        detail="Task is already taken or completed"
        )

    if task.user_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Task already has an owner"
        )
    task.user_id = user.id
    task.status = "in progress"
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{task_id}/complete")
def complete_task(session: Session = Depends(get_session),
                   task: Task = Depends(require_in_progress_owner)):
    task.status = "done"
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.patch("/{task_id}/release")
def release_task(task: Task = Depends(require_in_progress_owner), 
                 session: Session = Depends(get_session)):
    task.status = "free"
    task.user_id = None
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
