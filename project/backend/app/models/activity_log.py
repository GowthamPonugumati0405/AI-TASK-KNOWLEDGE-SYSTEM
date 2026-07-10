from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)  # login, task_update, document_upload, search
    details = Column(Text, nullable=True)  # free-text / JSON string with extra context
    created_at = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User", back_populates="activity_logs")
