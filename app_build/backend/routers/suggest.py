"""
NoteFlow AI — Suggestions Router
POST /api/suggest/* — Summarize, Simplify, Revision Questions.
Supports batch processing with optional batch parameter for free tier limits.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/suggest", tags=["Suggestions"])


class SuggestRequest(BaseModel):
    note_id: str
    batch: int = 0  # Batch number: 0, 1, 2... each processes 3 chunks


@router.post("/summarize")
async def summarize_note(req: SuggestRequest):
    """Generate a summary for pages in a note."""
    try:
        from backend.services.suggestions import summarize
        result = summarize(req.note_id, batch=req.batch)
        return {
            "note_id": req.note_id,
            "type": "summary",
            "content": result["content"],
            "start_page": result["start_page"],
            "end_page": result["end_page"],
            "total_pages": result["total_pages"],
            "has_next": result["has_next"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simplify")
async def simplify_note(req: SuggestRequest):
    """Generate a simplified version of pages in a note."""
    try:
        from backend.services.suggestions import simplify
        result = simplify(req.note_id, batch=req.batch)
        return {
            "note_id": req.note_id,
            "type": "simplification",
            "content": result["content"],
            "start_page": result["start_page"],
            "end_page": result["end_page"],
            "total_pages": result["total_pages"],
            "has_next": result["has_next"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revise")
async def revise_note(req: SuggestRequest):
    """Generate revision questions from pages in a note."""
    try:
        from backend.services.suggestions import generate_revision
        result = generate_revision(req.note_id, batch=req.batch)
        return {
            "note_id": req.note_id,
            "type": "revision_questions",
            "content": result["content"],
            "start_page": result["start_page"],
            "end_page": result["end_page"],
            "total_pages": result["total_pages"],
            "has_next": result["has_next"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

