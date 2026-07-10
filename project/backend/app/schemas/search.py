from typing import List

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResultItem(BaseModel):
    document_id: int
    document_title: str
    chunk_text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
