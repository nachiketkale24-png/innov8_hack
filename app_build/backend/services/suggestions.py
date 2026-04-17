"""
NoteFlow AI — Suggestion Service
AI-powered summarization, simplification, and revision question generation.
"""

from datetime import datetime, timezone

from backend.database import chunks_col, notes_col, activity_col
from backend.config import GEMINI_CONTEXT_CHUNKS


def _get_note_context(note_id: str) -> str:
    """
    Retrieve chunks for a note and build a context string.
    Limits to GEMINI_CONTEXT_CHUNKS (top 3) to avoid token overflow.
    """
    chunks = list(
        chunks_col.find({"note_id": note_id})
        .sort("chunk_index", 1)
        .limit(GEMINI_CONTEXT_CHUNKS)
    )
    if not chunks:
        raise ValueError(f"No chunks found for note_id: {note_id}")
    return "\n---\n".join(c["text"] for c in chunks)


def _log_activity(action: str, note_id: str, details: str) -> None:
    """Log a suggestion activity event."""
    activity_col.insert_one({
        "action": action,
        "note_id": note_id,
        "details": details,
        "timestamp": datetime.now(timezone.utc),
    })


def summarize(note_id: str) -> str:
    """Generate a summary for the given note."""
    from ai.gemini_client import generate_text
    from ai.prompts import SUMMARIZE_SYSTEM, SUMMARIZE_USER

    context = _get_note_context(note_id)
    result = generate_text(
        SUMMARIZE_SYSTEM,
        SUMMARIZE_USER.format(context=context),
    )
    _log_activity("summarize", note_id, "Generated summary")
    return result


def simplify(note_id: str) -> str:
    """Generate a simplified explanation for the given note."""
    from ai.gemini_client import generate_text
    from ai.prompts import SIMPLIFY_SYSTEM, SIMPLIFY_USER

    context = _get_note_context(note_id)
    result = generate_text(
        SIMPLIFY_SYSTEM,
        SIMPLIFY_USER.format(context=context),
    )
    _log_activity("simplify", note_id, "Generated simplification")
    return result


def generate_revision(note_id: str) -> str:
    """Generate revision questions for the given note."""
    from ai.gemini_client import generate_text
    from ai.prompts import REVISE_SYSTEM, REVISE_USER

    context = _get_note_context(note_id)
    result = generate_text(
        REVISE_SYSTEM,
        REVISE_USER.format(context=context),
    )
    _log_activity("revise", note_id, "Generated revision questions")
    return result
