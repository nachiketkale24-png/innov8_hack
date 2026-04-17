"""
NoteFlow AI — Learning Plan Pydantic Models
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class WeekPlan(BaseModel):
    """Single week inside a learning roadmap."""
    week: int
    title: str
    tasks: List[str]
    linked_note_ids: List[str] = []


class PlanCreate(BaseModel):
    """Body for POST /api/planner/create."""
    goal: str
    timeframe: str = "flexible"


class PlanOut(BaseModel):
    """Plan document returned by the API."""
    id: str = Field(alias="_id")
    goal: str
    roadmap: List[WeekPlan]
    created_at: datetime

    class Config:
        populate_by_name = True
