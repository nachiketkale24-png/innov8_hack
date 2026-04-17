"""
NoteFlow AI — Streamlit Frontend Utilities
HTTP client helpers for communicating with the FastAPI backend.
"""

import os
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# ── Low-level helpers ────────────────────────────────────

def api_get(endpoint: str, params: dict = None) -> dict:
    """Make a GET request to the backend. Raises on HTTP error."""
    resp = requests.get(f"{BACKEND_URL}{endpoint}", params=params, timeout=30)
    _raise_with_detail(resp)
    return resp.json()


def api_post(endpoint: str, json_data: dict = None, files: dict = None) -> dict:
    """Make a POST request to the backend. Raises on HTTP error."""
    resp = requests.post(
        f"{BACKEND_URL}{endpoint}",
        json=json_data,
        files=files,
        timeout=60,
    )
    _raise_with_detail(resp)
    return resp.json()


def api_delete(endpoint: str) -> dict:
    """Make a DELETE request to the backend. Raises on HTTP error."""
    resp = requests.delete(f"{BACKEND_URL}{endpoint}", timeout=30)
    _raise_with_detail(resp)
    return resp.json()


def _raise_with_detail(resp: requests.Response) -> None:
    """Raise an exception with backend error detail if available."""
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(f"[{resp.status_code}] {detail}")


# ── Domain-specific helpers ──────────────────────────────

def upload_pdf(file_name: str, file_bytes: bytes) -> dict:
    """
    Upload a PDF file to /api/ingest/pdf.
    Returns the response dict with 'message' and 'note' keys.
    """
    return api_post(
        "/api/ingest/pdf",
        files={"file": (file_name, file_bytes, "application/pdf")},
    )


def search(query: str, top_k: int = 5) -> list:
    """
    Semantic search via /api/search.
    Returns a list of result dicts (chunk_text, note_title, similarity_score, etc.)
    """
    data = api_post("/api/search", json_data={"query": query, "top_k": top_k})
    return data.get("results", [])
