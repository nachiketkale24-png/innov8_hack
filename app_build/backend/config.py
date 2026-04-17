"""
NoteFlow AI — Configuration
Loads environment variables and provides app-wide settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Gemini API ──────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_EMBED_MODEL: str = "models/text-embedding-004"
GEMINI_LLM_MODEL: str = "gemini-2.0-flash"

# ── MongoDB ─────────────────────────────────────────────
MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "noteflow_ai")

# ── FAISS ───────────────────────────────────────────────
FAISS_INDEX_PATH: str = os.getenv(
    "FAISS_INDEX_PATH",
    os.path.join(os.path.dirname(__file__), "faiss_store", "index.faiss"),
)

# ── Chunking ────────────────────────────────────────────
CHUNK_SIZE: int = 900          # characters per chunk (target ~800-1000)
CHUNK_OVERLAP: int = 100       # character overlap between consecutive chunks

# ── Retrieval ───────────────────────────────────────────
FAISS_TOP_K: int = 5           # retrieve top-5 from FAISS
GEMINI_CONTEXT_CHUNKS: int = 3 # only top-3 chunks sent to Gemini

# ── Server ──────────────────────────────────────────────
BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
