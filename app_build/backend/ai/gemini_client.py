"""
NoteFlow AI — Gemini API Client
Wrapper for embedding and text generation via Google Gemini.
"""

import numpy as np

from backend.config import GEMINI_API_KEY, GEMINI_EMBED_MODEL, GEMINI_LLM_MODEL

# ── Lazy Gemini SDK import ──────────────────────────────
try:
    from google import genai
    from google.genai import types
    _genai_available = True
except ImportError:
    genai = None  # type: ignore
    types = None  # type: ignore
    _genai_available = False

# ── Lazy client (initialized on first call) ─────────────
_client = None


def _get_client():
    """Get or create the Gemini client (lazy init)."""
    global _client
    if not _genai_available:
        raise RuntimeError(
            "google-genai SDK is not installed. "
            "Install it with: pip install google-genai"
        )
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Add it to your .env file."
        )
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def get_embedding(text: str) -> np.ndarray:
    """
    Embed a single text string using Gemini embedding model.
    Returns a 768-dim float32 numpy array.
    """
    client = _get_client()
    result = client.models.embed_content(
        model=GEMINI_EMBED_MODEL,
        contents=text,
    )
    return np.array(result.embeddings[0].values, dtype=np.float32)


def get_embeddings_batch(texts: list[str]) -> np.ndarray:
    """
    Embed a batch of texts. Returns an (N, 768) float32 numpy array.
    """
    client = _get_client()
    result = client.models.embed_content(
        model=GEMINI_EMBED_MODEL,
        contents=texts,
    )
    return np.array(
        [e.values for e in result.embeddings], dtype=np.float32
    )


def generate_text(system_prompt: str, user_prompt: str) -> str:
    """
    Generate text using Gemini LLM with a system + user prompt pair.
    Returns the generated text as a string.
    """
    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_LLM_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=2048,
        ),
    )
    return response.text

