"""
NoteFlow AI — Search Router
POST /api/search — Semantic search across all notes.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId

from backend.database import chunks_col, notes_col, activity_col
from backend.config import FAISS_TOP_K

router = APIRouter(prefix="/api", tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = FAISS_TOP_K


@router.post("/search")
async def semantic_search(req: SearchRequest):
    """
    Semantic search across all ingested notes.
    FAISS retrieves top-k, results are returned with chunk text and metadata.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Lazy imports — these depend on FAISS + Gemini SDK
    try:
        from backend.ai.gemini_client import get_embedding
        from backend.services.memory import search as faiss_search
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Search dependencies not available: {e}",
        )

    # Embed the query
    query_vec = get_embedding(req.query)

    # FAISS search
    results = faiss_search(query_vec, top_k=req.top_k)

    if not results:
        return {"results": [], "message": "No matching notes found."}

    # Resolve FAISS IDs → MongoDB chunks
    search_results = []
    for fid, score in results:
        chunk = chunks_col.find_one({"faiss_index_id": fid})
        if not chunk:
            continue

        note = notes_col.find_one({"_id": ObjectId(chunk["note_id"])})
        search_results.append({
            "chunk_text": chunk["text"],
            "page_number": chunk["page_number"],
            "note_id": chunk["note_id"],
            "note_title": note["title"] if note else "Unknown",
            "similarity_score": round(score, 4),
            "faiss_index_id": fid,
        })

    # Log search activity
    activity_col.insert_one({
        "action": "search",
        "note_id": None,
        "details": f"Searched: '{req.query}' ({len(search_results)} results)",
        "timestamp": datetime.now(timezone.utc),
    })

    return {"results": search_results}

