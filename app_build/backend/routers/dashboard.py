"""
NoteFlow AI — Dashboard Router
GET /api/score    — Understanding Score
GET /api/activity — Recent activity log
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/score")
async def get_score():
    """Get the current Understanding Score."""
    from backend.services.scoring import compute_score
    return compute_score()


@router.get("/activity")
async def get_activity():
    """Get the 20 most recent activity events."""
    from backend.database import activity_col
    events = list(activity_col.find().sort("timestamp", -1).limit(20))
    for e in events:
        e["_id"] = str(e["_id"])
    return {"activity": events}

