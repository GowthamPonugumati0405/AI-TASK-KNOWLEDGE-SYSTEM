from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: int


class TaskUpdateStatus(BaseModel):
    status: TaskStatus


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    assigned_to: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
