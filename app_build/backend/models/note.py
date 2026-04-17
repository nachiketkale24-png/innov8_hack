"""
NoteFlow AI — Note & Chunk Pydantic Models
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """Metadata returned after PDF ingestion."""
    filename: str
    title: str
    total_pages: int
    total_chunks: int


class NoteOut(BaseModel):
    """Note document returned by the API."""
    id: str = Field(alias="_id")
    filename: str
    title: str
    total_pages: int
    total_chunks: int
    uploaded_at: datetime
    tags: List[str] = []

    class Config:
        populate_by_name = True


class ChunkOut(BaseModel):
    """Single chunk returned by the API."""
    id: str = Field(alias="_id")
    note_id: str
    chunk_index: int
    text: str
    page_number: int
    char_count: int
    faiss_index_id: int

    class Config:
        populate_by_name = True


class NoteDetail(BaseModel):
    """Full note with its chunks."""
    note: NoteOut
    chunks: List[ChunkOut]


class SearchRequest(BaseModel):
    """Body for POST /api/search."""
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    """Single search hit."""
    chunk_text: str
    page_number: int
    note_id: str
    note_title: str
    similarity_score: float
    faiss_index_id: int
