import enum

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class TaskStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending, nullable=False, index=True)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    assignee = relationship("User", back_populates="tasks_assigned", foreign_keys=[assigned_to])
    creator = relationship("User", back_populates="tasks_created", foreign_keys=[created_by])
