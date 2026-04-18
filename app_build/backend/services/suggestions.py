"""
NoteFlow AI — Suggestion Service
AI-powered summarization, simplification, and revision question generation.
Supports page-based batching for better UX (e.g., "Pages 1-4", "Pages 5-8").
"""

from datetime import datetime, timezone

from backend.database import chunks_col, notes_col, activity_col
from backend.config import PAGES_PER_BATCH


def _get_page_batch_context(note_id: str, batch: int = 0) -> dict:
    """
    Retrieve chunks from a page range and build a context string.
    Groups by page numbers: batch 0 = pages 1-4, batch 1 = pages 5-8, etc.
    
    Args:
        note_id: MongoDB note ID
        batch: Batch number (0, 1, 2...) - each batch covers PAGES_PER_BATCH pages
    
    Returns:
        {
            'context': context_string,
            'start_page': int,
            'end_page': int,
            'total_pages': int,
            'has_next': bool,
        }
    """
    # Get all chunks for this note
    all_chunks = list(
        chunks_col.find({"note_id": note_id})
        .sort("chunk_index", 1)
    )
    if not all_chunks:
        raise ValueError(f"No chunks found for note_id: {note_id}")
    
    # Get unique page numbers
    unique_pages = sorted(set(c["page_number"] for c in all_chunks))
    total_pages = len(unique_pages)
    
    # Calculate page range for this batch
    start_page_idx = batch * PAGES_PER_BATCH
    end_page_idx = start_page_idx + PAGES_PER_BATCH
    
    # Get pages for this batch
    batch_pages = unique_pages[start_page_idx:end_page_idx]
    if not batch_pages:
        raise ValueError(f"No pages available for batch {batch}")
    
    start_page = batch_pages[0]
    end_page = batch_pages[-1]
    
    # Get all chunks from these pages
    batch_chunks = [c for c in all_chunks if c["page_number"] in batch_pages]
    
    # Build context string
    context = "\n---\n".join(c["text"] for c in batch_chunks)
    
    # Check if more batches available
    has_next = end_page_idx < total_pages
    
    return {
        "context": context,
        "start_page": start_page,
        "end_page": end_page,
        "total_pages": total_pages,
        "has_next": has_next,
    }


def _log_activity(action: str, note_id: str, details: str) -> None:
    """Log a suggestion activity event."""
    activity_col.insert_one({
        "action": action,
        "note_id": note_id,
        "details": details,
        "timestamp": datetime.now(timezone.utc),
    })


def summarize(note_id: str, batch: int = 0) -> dict:
    """Generate a summary for pages in a note."""
    from backend.ai.gemini_client import generate_text
    from backend.ai.prompts import SUMMARIZE_SYSTEM, SUMMARIZE_USER

    page_info = _get_page_batch_context(note_id, batch)
    result = generate_text(
        SUMMARIZE_SYSTEM,
        SUMMARIZE_USER.format(context=page_info["context"]),
    )
    _log_activity("summarize", note_id, f"Generated summary (pages {page_info['start_page']}-{page_info['end_page']})")
    
    return {
        "content": result,
        "start_page": page_info["start_page"],
        "end_page": page_info["end_page"],
        "total_pages": page_info["total_pages"],
        "has_next": page_info["has_next"],
    }


def simplify(note_id: str, batch: int = 0) -> dict:
    """Generate a simplified explanation for pages in a note."""
    from backend.ai.gemini_client import generate_text
    from backend.ai.prompts import SIMPLIFY_SYSTEM, SIMPLIFY_USER

    page_info = _get_page_batch_context(note_id, batch)
    result = generate_text(
        SIMPLIFY_SYSTEM,
        SIMPLIFY_USER.format(context=page_info["context"]),
    )
    _log_activity("simplify", note_id, f"Generated simplification (pages {page_info['start_page']}-{page_info['end_page']})")
    
    return {
        "content": result,
        "start_page": page_info["start_page"],
        "end_page": page_info["end_page"],
        "total_pages": page_info["total_pages"],
        "has_next": page_info["has_next"],
    }


def generate_revision(note_id: str, batch: int = 0) -> dict:
    """Generate revision questions from pages in a note."""
    from backend.ai.gemini_client import generate_text
    from backend.ai.prompts import REVISE_SYSTEM, REVISE_USER

    page_info = _get_page_batch_context(note_id, batch)
    result = generate_text(
        REVISE_SYSTEM,
        REVISE_USER.format(context=page_info["context"]),
    )
    _log_activity("revise", note_id, f"Generated revision questions (pages {page_info['start_page']}-{page_info['end_page']})")
    
    return {
        "content": result,
        "start_page": page_info["start_page"],
        "end_page": page_info["end_page"],
        "total_pages": page_info["total_pages"],
        "has_next": page_info["has_next"],
    }
