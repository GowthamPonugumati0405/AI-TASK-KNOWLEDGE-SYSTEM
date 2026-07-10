from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    content_preview = Column(Text, nullable=True)  # first N chars, for admin UI

    # index of this doc's chunks inside the FAISS store starts here;
    # chunk_count lets us know how many vector ids belong to this document
    vector_start_id = Column(Integer, nullable=False)
    chunk_count = Column(Integer, nullable=False, default=0)

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    uploader = relationship("User", back_populates="documents")
