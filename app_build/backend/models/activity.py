"""
NoteFlow AI — Activity Log Pydantic Models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ActivityCreate(BaseModel):
    """Internal model for logging an activity event."""
    action: str          # search | summarize | simplify | revise | plan_create | pdf_upload
    note_id: Optional[str] = None
    details: str = ""


class ActivityOut(BaseModel):
    """Activity event returned by the API."""
    id: str = Field(alias="_id")
    action: str
    note_id: Optional[str] = None
    details: str
    timestamp: datetime

    class Config:
        populate_by_name = True


class ScoreOut(BaseModel):
    """Understanding Score response."""
    score: int
    breakdown: dict
