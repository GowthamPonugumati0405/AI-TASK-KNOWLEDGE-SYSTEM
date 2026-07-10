"""
Thin persistence wrapper around a FAISS index.

Design notes (why it's built this way):
- We use IndexFlatIP (inner product) over L2-normalized vectors, which is
  mathematically equivalent to cosine similarity search. This keeps the
  core retrieval logic transparent instead of hiding it behind an LLM API.
- Alongside the FAISS index we keep a parallel metadata list (documents.json)
  so every vector id maps back to (document_id, document_title, chunk_text).
  FAISS itself only stores vectors + integer ids, not text, so this side
  store is required.
- Both files are persisted to disk under VECTOR_INDEX_DIR so the index
  survives a server restart without needing to re-embed every document.
"""
import json
import os
import threading
from typing import List, Tuple

import faiss
import numpy as np

from app.config import settings

_LOCK = threading.Lock()


class VectorStore:
    def __init__(self):
        self.index_path = os.path.join(settings.VECTOR_INDEX_DIR, "faiss.index")
        self.meta_path = os.path.join(settings.VECTOR_INDEX_DIR, "metadata.json")
        self.dim = settings.EMBEDDING_DIM

        self.index = faiss.IndexFlatIP(self.dim)
        self.metadata: List[dict] = []  # position i corresponds to vector id i

        self._load()

    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

    def _persist(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        return vectors / norms

    def add(self, vectors: np.ndarray, chunk_meta: List[dict]) -> int:
        """Adds vectors + metadata, returns the starting vector id assigned."""
        with _LOCK:
            start_id = self.index.ntotal
            vectors = self._normalize(vectors.astype("float32"))
            self.index.add(vectors)
            self.metadata.extend(chunk_meta)
            self._persist()
            return start_id

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[dict, float]]:
        if self.index.ntotal == 0:
            return []
        query_vector = self._normalize(query_vector.astype("float32").reshape(1, -1))
        scores, ids = self.index.search(query_vector, min(top_k, self.index.ntotal))
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:
                continue
            results.append((self.metadata[idx], float(score)))
        return results


vector_store = VectorStore()
