"""
NoteFlow AI — Planner Router
POST /api/planner/create  — Create a learning roadmap
GET  /api/planner          — List all plans
GET  /api/planner/{id}     — Get a single plan
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId

from backend.database import plans_col

router = APIRouter(prefix="/api/planner", tags=["Planner"])


class PlanRequest(BaseModel):
    goal: str
    timeframe: str = "flexible"


@router.post("/create")
async def create_learning_plan(req: PlanRequest):
    """Create a learning roadmap from a goal."""
    try:
        from backend.services.planner import create_plan
        plan = create_plan(req.goal, req.timeframe)
        return {"status": "success", "plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan creation failed: {str(e)}")


@router.get("")
async def list_plans():
    """List all saved learning plans."""
    plans = list(plans_col.find().sort("created_at", -1))
    for p in plans:
        p["_id"] = str(p["_id"])
    return {"plans": plans}


@router.get("/{plan_id}")
async def get_plan(plan_id: str):
    """Get a specific learning plan."""
    try:
        plan = plans_col.find_one({"_id": ObjectId(plan_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid plan ID format.")

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")

    plan["_id"] = str(plan["_id"])
    return {"plan": plan}
