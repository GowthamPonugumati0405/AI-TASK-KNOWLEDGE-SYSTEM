from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.database import get_db
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdateStatus
from app.services.activity_service import log_activity

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    assignee = db.query(User).filter(User.id == payload.assigned_to).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assigned user not found")

    task = Task(
        title=payload.title,
        description=payload.description,
        assigned_to=payload.assigned_to,
        created_by=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    log_activity(db, current_user.id, "task_create", f"created task {task.id} for user {assignee.id}")
    return task


@router.get("/", response_model=List[TaskOut])
def list_tasks(
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dynamic filtering API: /tasks?status=completed  /tasks?assigned_to=1
    Regular users only ever see their own tasks; admins can see everyone's
    and additionally filter by assigned_to.
    """
    query = db.query(Task)

    if current_user.role.name != "admin":
        query = query.filter(Task.assigned_to == current_user.id)
    elif assigned_to is not None:
        query = query.filter(Task.assigned_to == assigned_to)

    if status is not None:
        query = query.filter(Task.status == status)

    return query.order_by(Task.created_at.desc()).all()


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role.name != "admin" and task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own tasks")

    task.status = payload.status
    db.commit()
    db.refresh(task)

    log_activity(
        db, current_user.id, "task_update", f"task {task.id} status -> {payload.status.value}"
    )
    return task
