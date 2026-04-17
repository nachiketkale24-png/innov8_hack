"""
NoteFlow AI — Suggestions Router
POST /api/suggest/* — Summarize, Simplify, Revision Questions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/suggest", tags=["Suggestions"])


class SuggestRequest(BaseModel):
    note_id: str


@router.post("/summarize")
async def summarize_note(req: SuggestRequest):
    """Generate a summary for a note's content."""
    try:
        from backend.services.suggestions import summarize
        result = summarize(req.note_id)
        return {"note_id": req.note_id, "type": "summary", "content": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simplify")
async def simplify_note(req: SuggestRequest):
    """Generate a simplified version of a note's content."""
    try:
        from backend.services.suggestions import simplify
        result = simplify(req.note_id)
        return {"note_id": req.note_id, "type": "simplification", "content": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revise")
async def revise_note(req: SuggestRequest):
    """Generate revision questions from a note's content."""
    try:
        from backend.services.suggestions import generate_revision
        result = generate_revision(req.note_id)
        return {"note_id": req.note_id, "type": "revision_questions", "content": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

