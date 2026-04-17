"""
NoteFlow AI — Notes Router
GET/DELETE /api/notes endpoints.
"""

from fastapi import APIRouter, HTTPException
from bson import ObjectId

from backend.database import notes_col, chunks_col

router = APIRouter(prefix="/api/notes", tags=["Notes"])


@router.get("")
async def list_notes():
    """List all ingested notes (metadata only)."""
    notes = list(notes_col.find().sort("uploaded_at", -1))
    for n in notes:
        n["_id"] = str(n["_id"])
    return {"notes": notes}


@router.get("/{note_id}")
async def get_note(note_id: str):
    """Get a specific note with all its chunks."""
    try:
        note = notes_col.find_one({"_id": ObjectId(note_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID format.")

    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    note["_id"] = str(note["_id"])
    chunks = list(chunks_col.find({"note_id": note_id}).sort("chunk_index", 1))
    for c in chunks:
        c["_id"] = str(c["_id"])

    return {"note": note, "chunks": chunks}


@router.delete("/{note_id}")
async def delete_note(note_id: str):
    """Delete a note and its associated chunks."""
    try:
        result = notes_col.delete_one({"_id": ObjectId(note_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid note ID format.")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found.")

    # Delete associated chunks (FAISS vectors remain but become orphaned — acceptable for MVP)
    chunks_col.delete_many({"note_id": note_id})

    return {"status": "success", "message": f"Note {note_id} deleted."}


@router.get("/{note_id}/related")
async def get_related_notes(note_id: str):
    """Get notes related to a specific note using its first chunk as query."""
    from ai.gemini_client import get_embedding
    from backend.services.memory import search as faiss_search

    # Get the first chunk of this note
    chunk = chunks_col.find_one({"note_id": note_id}, sort=[("chunk_index", 1)])
    if not chunk:
        raise HTTPException(status_code=404, detail="No chunks found for this note.")

    # Embed and search
    query_vec = get_embedding(chunk["text"])
    results = faiss_search(query_vec, top_k=5)

    # Resolve chunks and filter out same-note results
    related = []
    seen_notes = set()
    for fid, score in results:
        c = chunks_col.find_one({"faiss_index_id": fid})
        if not c or c["note_id"] == note_id:
            continue
        if c["note_id"] in seen_notes:
            continue
        seen_notes.add(c["note_id"])
        note = notes_col.find_one({"_id": ObjectId(c["note_id"])})
        related.append({
            "note_id": c["note_id"],
            "note_title": note["title"] if note else "Unknown",
            "similarity_score": round(score, 4),
        })

    return {"related_notes": related}
