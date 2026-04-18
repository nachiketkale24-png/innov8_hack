"""
NoteFlow AI — Database Layer
MongoDB connection and collection accessors.
"""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from backend.config import MONGODB_URI, MONGODB_DB_NAME

# ── Connection ──────────────────────────────────────────
_client: MongoClient = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
db: Database = _client[MONGODB_DB_NAME]

# ── Collections ─────────────────────────────────────────
notes_col: Collection = db["notes"]
chunks_col: Collection = db["chunks"]
plans_col: Collection = db["plans"]
activity_col: Collection = db["activity_log"]

# ── Indexes (idempotent) ────────────────────────────────
try:
    chunks_col.create_index("faiss_index_id", unique=True)
    chunks_col.create_index("note_id")
    activity_col.create_index("timestamp")
except Exception as e:
    print(f"[WARN] Could not connect to MongoDB for indexes: {e}")


def get_db() -> Database:
    """Return the database instance (for dependency injection)."""
    return db
