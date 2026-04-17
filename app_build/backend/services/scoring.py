"""
NoteFlow AI — Scoring Service
Understanding Score computation: simple additive scoring capped at 100.
"""

from backend.database import activity_col, notes_col


def compute_score() -> dict:
    """
    Compute the Understanding Score.
    Formula: raw = (notes×5) + (queries×3) + (suggestions×4) + (planner×8)
    Final  = min(raw, 100)
    Returns {"score": int, "breakdown": dict}.
    """
    notes_uploaded = notes_col.count_documents({})
    queries_made = activity_col.count_documents({"action": "search"})
    suggestions_used = activity_col.count_documents({
        "action": {"$in": ["summarize", "simplify", "revise"]}
    })
    planner_interactions = activity_col.count_documents({"action": "plan_create"})

    raw_score = (
        notes_uploaded * 5
        + queries_made * 3
        + suggestions_used * 4
        + planner_interactions * 8
    )
    final_score = min(raw_score, 100)

    return {
        "score": final_score,
        "breakdown": {
            "notes_uploaded": notes_uploaded,
            "queries_made": queries_made,
            "suggestions_used": suggestions_used,
            "planner_interactions": planner_interactions,
            "raw_score": raw_score,
        },
    }
