"""
NoteFlow AI — Streamlit Main Application Entry Point
Run: streamlit run app.py  (from inside app_build/frontend/)
"""

import sys
import os

# Ensure utils.py (in same directory) is always importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(
    page_title="NoteFlow AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ─────────────────────────────────────────────
st.sidebar.title("🧠 NoteFlow AI")
st.sidebar.caption("AI-Powered Learning Assistant")
st.sidebar.divider()
st.sidebar.markdown(
    """
**Pages:**
- 📄 Upload PDFs
- 🔍 Explore & Search
- 💡 AI Suggestions
- 🎯 Learning Planner
- 📊 Dashboard & Score
"""
)

# ── Home Page ────────────────────────────────────────────
st.title("🧠 NoteFlow AI")
st.subheader("Transform your static notes into an intelligent learning system")
st.divider()

st.markdown("""
**Getting Started:**

1. **📄 Upload** — Drop in your PDF study materials
2. **🔍 Explore** — Search your notes with natural language
3. **💡 Suggestions** — Get AI summaries, simplifications & revision questions
4. **🎯 Planner** — Set a learning goal and get a structured roadmap
5. **📊 Dashboard** — Track your Understanding Score

*Use the sidebar to navigate between pages.*
""")

# ── Backend Health Check ─────────────────────────────────
st.divider()
st.subheader("🔌 System Status")
try:
    from utils import api_get
    health = api_get("/health")
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Notes", health.get("notes_count", 0))
    col2.metric("🧩 Chunks", health.get("chunks_count", 0))
    col3.metric("🔢 Vectors", health.get("faiss_vectors", 0))
    st.success("Backend connected ✅")
except Exception:
    st.info("⚡ Backend not running — start it with: `uvicorn main:app --reload` from `app_build/backend/`")
