from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.activity_service import log_activity
from app.services.embedding_service import embed_query
from app.services.vector_store import vector_store

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
def semantic_search(
    payload: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    query text -> embedding -> FAISS cosine-similarity lookup -> ranked chunks.
    No external LLM call is used for retrieval itself.
    """
    query_vector = embed_query(payload.query)
    raw_results = vector_store.search(query_vector, top_k=payload.top_k)

    results = [
        SearchResultItem(
            document_id=meta["document_id"],
            document_title=meta["document_title"],
            chunk_text=meta["chunk_text"],
            score=score,
        )
        for meta, score in raw_results
    ]

    log_activity(db, current_user.id, "search", payload.query)

    return SearchResponse(query=payload.query, results=results)
