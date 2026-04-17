"""
NoteFlow AI — Planner Service
Goal-based learning roadmap generation via Gemini.
"""

import json
from datetime import datetime, timezone

from backend.database import notes_col, plans_col, activity_col


def create_plan(goal: str, timeframe: str = "flexible") -> dict:
    """
    Generate a learning roadmap from a user goal.
    Uses all available note titles as context for Gemini.
    Returns the saved plan document.
    """
    # Gather all note titles for context
    notes = list(notes_col.find({}, {"title": 1, "total_chunks": 1, "total_pages": 1}))
    if notes:
        notes_context = "\n".join(
            f"- {n['title']} ({n['total_pages']} pages, {n['total_chunks']} chunks)"
            for n in notes
        )
    else:
        notes_context = "(No notes uploaded yet)"

    # Lazy imports — Gemini only needed at call time
    from backend.ai.gemini_client import generate_text
    from backend.ai.prompts import PLANNER_SYSTEM, PLANNER_USER

    # Call Gemini
    raw = generate_text(
        PLANNER_SYSTEM,
        PLANNER_USER.format(
            goal=goal,
            timeframe=timeframe,
            notes_context=notes_context,
        ),
    )

    # Parse the JSON response
    try:
        # Strip markdown fences if Gemini wraps them
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        roadmap = json.loads(cleaned.strip())
    except (json.JSONDecodeError, IndexError):
        # Fallback: create a simple roadmap from the raw text
        roadmap = [
            {
                "week": 1,
                "title": "Study Plan",
                "tasks": [raw[:500]],
                "linked_note_ids": [],
            }
        ]

    # Save to MongoDB
    plan_doc = {
        "goal": goal,
        "roadmap": roadmap,
        "created_at": datetime.now(timezone.utc),
    }
    result = plans_col.insert_one(plan_doc)
    plan_doc["_id"] = str(result.inserted_id)

    # Log activity
    activity_col.insert_one({
        "action": "plan_create",
        "note_id": None,
        "details": f"Created plan: {goal}",
        "timestamp": datetime.now(timezone.utc),
    })

    return plan_doc
