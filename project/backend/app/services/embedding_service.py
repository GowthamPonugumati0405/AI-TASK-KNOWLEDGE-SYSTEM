"""
Core AI logic for the assignment: text -> chunks -> embeddings -> FAISS.

We deliberately do NOT call any external LLM API for search. Embeddings are
generated locally with a sentence-transformers model (downloaded once from
HuggingFace, then cached on disk and reused). Chunking, normalization and
similarity search are all implemented in our own code (see vector_store.py),
not delegated to a hosted "search" endpoint.
"""
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> List[str]:
    """
    Simple word-based sliding-window chunker.
    chunk_size / overlap are in words, not tokens - kept simple and dependency-free.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings


def embed_query(query: str) -> np.ndarray:
    model = get_model()
    return model.encode([query], convert_to_numpy=True, show_progress_bar=False)[0]
