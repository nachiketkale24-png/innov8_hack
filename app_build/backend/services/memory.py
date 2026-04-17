"""
NoteFlow AI — Memory Service
FAISS index management: add vectors, search, persist/load from disk.
"""

import os
import numpy as np

from backend.config import FAISS_INDEX_PATH, FAISS_TOP_K

# ── FAISS import (graceful if not installed) ────────────
try:
    import faiss
    _faiss_available = True
except ImportError:
    faiss = None  # type: ignore
    _faiss_available = False

# ── Embedding dimension (Gemini text-embedding-004) ─────
EMBED_DIM = 768

# ── Global FAISS index ──────────────────────────────────
_index = None
_next_id: int = 0


def _ensure_dir() -> None:
    """Create the faiss_store directory if it doesn't exist."""
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)


def load_index() -> None:
    """Load the FAISS index from disk, or create a new one."""
    global _index, _next_id
    if not _faiss_available:
        return
    if os.path.exists(FAISS_INDEX_PATH):
        _index = faiss.read_index(FAISS_INDEX_PATH)
        _next_id = _index.ntotal
    else:
        _index = faiss.IndexFlatIP(EMBED_DIM)
        _next_id = 0


def save_index() -> None:
    """Persist the current FAISS index to disk."""
    if not _faiss_available or _index is None:
        return
    _ensure_dir()
    faiss.write_index(_index, FAISS_INDEX_PATH)


def add_vectors(vectors: np.ndarray) -> list[int]:
    """
    Add vectors to the FAISS index.
    Returns the list of faiss_index_ids assigned (sequential ints).
    These IDs are permanent and must be stored in MongoDB.
    """
    global _next_id
    if not _faiss_available:
        raise RuntimeError("FAISS is not installed. Cannot add vectors.")
    if _index is None:
        load_index()

    # Normalize for inner-product (cosine similarity)
    faiss.normalize_L2(vectors)

    n = vectors.shape[0]
    ids = list(range(_next_id, _next_id + n))
    _index.add(vectors)  # type: ignore
    _next_id += n

    save_index()
    return ids


def search(query_vector: np.ndarray, top_k: int = FAISS_TOP_K) -> list[tuple[int, float]]:
    """
    Search the FAISS index with a query vector.
    Returns list of (faiss_index_id, similarity_score) tuples,
    sorted by descending similarity.
    """
    if not _faiss_available or _index is None or _index.ntotal == 0:
        return []

    # Normalize query for cosine similarity
    qv = query_vector.reshape(1, -1).copy()
    faiss.normalize_L2(qv)

    distances, indices = _index.search(qv, min(top_k, _index.ntotal))

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        results.append((int(idx), float(dist)))
    return results


def get_total_vectors() -> int:
    """Return the number of vectors in the index."""
    if not _faiss_available:
        return 0
    if _index is None:
        load_index()
    return _index.ntotal if _index else 0


# ── Auto-load on import (graceful) ─────────────────────
try:
    load_index()
except Exception as e:
    print(f"[WARN] Could not load FAISS index on startup: {e}")

