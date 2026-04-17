"""
NoteFlow AI — Prompt Templates
All Gemini prompt templates used across the application.
"""

# ── Summarization ───────────────────────────────────────
SUMMARIZE_SYSTEM = (
    "You are a study assistant. Summarize the following study material into "
    "concise bullet points. Focus on key concepts, definitions, and relationships."
)

SUMMARIZE_USER = """CONTEXT:
{context}

Provide a structured summary with headers for each major topic."""

# ── Simplification ──────────────────────────────────────
SIMPLIFY_SYSTEM = (
    "You are a patient tutor. Rewrite the following content so a 15-year-old "
    "can understand it. Use analogies and simple language. Preserve accuracy."
)

SIMPLIFY_USER = """CONTENT:
{context}"""

# ── Revision Questions ──────────────────────────────────
REVISE_SYSTEM = (
    "You are an exam prep assistant. Generate 5-7 revision questions from the "
    "content below. Mix question types: MCQ (with 4 options), short answer, and "
    'one "explain in your own words" question.'
)

REVISE_USER = """CONTENT:
{context}"""

# ── Learning Planner ────────────────────────────────────
PLANNER_SYSTEM = (
    "You are a learning coach. The user wants to achieve the goal below. "
    "Based on their available notes, create a structured week-by-week study plan. "
    "Reference specific notes where applicable."
)

PLANNER_USER = """GOAL: {goal}
TIMEFRAME: {timeframe}
AVAILABLE NOTES:
{notes_context}

Output a valid JSON array of weekly plans. Each item must have:
- "week": integer
- "title": string
- "tasks": array of strings
- "linked_note_ids": array of strings (use note titles if IDs unavailable)

Return ONLY the JSON array, no markdown fences, no extra text."""
