from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    filename: str
    content_preview: Optional[str]
    chunk_count: int
    uploaded_by: int
    created_at: datetime
