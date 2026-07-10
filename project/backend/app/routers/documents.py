import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user, require_role
from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentOut
from app.services.activity_service import log_activity
from app.services.embedding_service import chunk_text, embed_texts
from app.services.vector_store import vector_store

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".txt"}  # PDF optional/extendable later


@router.post("/", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .txt files are supported")

    raw_bytes = file.file.read()
    text = raw_bytes.decode("utf-8", errors="ignore")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Persist the raw file to disk with a unique name to avoid collisions
    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    # --- Core AI step: chunk -> embed -> store in FAISS ---
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No usable text found in document")

    embeddings = embed_texts(chunks)

    document = Document(
        title=file.filename,
        filename=stored_name,
        filepath=filepath,
        content_preview=text[:300],
        vector_start_id=0,  # set after we know the doc id, patched below
        chunk_count=len(chunks),
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    chunk_meta = [
        {
            "document_id": document.id,
            "document_title": document.title,
            "chunk_text": chunk,
        }
        for chunk in chunks
    ]
    start_id = vector_store.add(embeddings, chunk_meta)
    document.vector_start_id = start_id
    db.commit()
    db.refresh(document)

    log_activity(db, current_user.id, "document_upload", f"uploaded '{document.title}' ({len(chunks)} chunks)")
    return document


@router.get("/", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Document).order_by(Document.created_at.desc()).all()
