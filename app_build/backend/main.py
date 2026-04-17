"""
NoteFlow AI — FastAPI Application Entry Point
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import BACKEND_HOST, BACKEND_PORT

# ── App ─────────────────────────────────────────────────
app = FastAPI(
    title="NoteFlow AI",
    description="AI-Powered Learning Assistant — transforms static notes into an intelligent knowledge system.",
    version="1.0.0",
)

# ── CORS (allow Streamlit frontend) ─────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────
# Imports are wrapped so the app can start even if optional
# dependencies (FAISS, Gemini) are not yet installed.
try:
    from backend.routers.ingest import router as ingest_router
    app.include_router(ingest_router)
except Exception as e:
    print(f"[WARN] Could not load ingest router: {e}")

try:
    from backend.routers.notes import router as notes_router
    app.include_router(notes_router)
except Exception as e:
    print(f"[WARN] Could not load notes router: {e}")

try:
    from backend.routers.search import router as search_router
    app.include_router(search_router)
except Exception as e:
    print(f"[WARN] Could not load search router: {e}")

try:
    from backend.routers.suggest import router as suggest_router
    app.include_router(suggest_router)
except Exception as e:
    print(f"[WARN] Could not load suggest router: {e}")

try:
    from backend.routers.planner import router as planner_router
    app.include_router(planner_router)
except Exception as e:
    print(f"[WARN] Could not load planner router: {e}")

try:
    from backend.routers.dashboard import router as dashboard_router
    app.include_router(dashboard_router)
except Exception as e:
    print(f"[WARN] Could not load dashboard router: {e}")


@app.get("/")
async def root():
    return {
        "app": "NoteFlow AI",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    result = {"status": "healthy"}
    try:
        from backend.database import notes_col, chunks_col
        result["notes_count"] = notes_col.count_documents({})
        result["chunks_count"] = chunks_col.count_documents({})
    except Exception:
        result["notes_count"] = -1
        result["chunks_count"] = -1

    try:
        from backend.services.memory import get_total_vectors
        result["faiss_vectors"] = get_total_vectors()
    except Exception:
        result["faiss_vectors"] = -1

    return result


# ── Run ─────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
