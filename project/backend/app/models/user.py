from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    role = relationship("Role", back_populates="users")
    tasks_assigned = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assigned_to"
    )
    tasks_created = relationship(
        "Task", back_populates="creator", foreign_keys="Task.created_by"
    )
    documents = relationship("Document", back_populates="uploader")
    activity_logs = relationship("ActivityLog", back_populates="user")
