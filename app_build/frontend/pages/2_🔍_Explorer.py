"""
NoteFlow AI — 🔍 Explorer & Semantic Search Page
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import search, api_get

st.set_page_config(page_title="Explorer | NoteFlow AI", page_icon="🔍", layout="wide")
st.title("🔍 Note Explorer & Semantic Search")
st.markdown("Search your knowledge base using natural language.")

# ── Search ───────────────────────────────────────────────
query = st.text_input("What are you looking for?", placeholder="e.g., How does backpropagation work?")

if st.button("🔍 Search", type="primary") and query.strip():
    with st.spinner("Searching..."):
        try:
            results = search(query.strip(), top_k=5)
            if not results:
                st.warning("No results found. Try a different query or upload more notes.")
            else:
                st.success(f"Found **{len(results)}** relevant chunks")
                for i, r in enumerate(results, 1):
                    score = r.get("similarity_score", 0)
                    title = r.get("note_title", "Unknown")
                    page  = r.get("page_number", "?")
                    with st.expander(
                        f"#{i} — {title} (p.{page})  •  Score: {score:.2%}",
                        expanded=(i <= 3),
                    ):
                        st.markdown(r.get("chunk_text", ""))
                        st.caption(
                            f"Note: {title} | Page: {page} | "
                            f"FAISS ID: {r.get('faiss_index_id', 'N/A')}"
                        )
        except Exception as e:
            st.error(f"Search failed: {e}")

# ── Browse Notes ─────────────────────────────────────────
st.divider()
st.subheader("📚 Browse All Notes")

try:
    notes = api_get("/api/notes").get("notes", [])
    if not notes:
        st.info("No notes yet. Upload a PDF first!")
    else:
        for note in notes:
            with st.expander(f"📄 {note['title']} — {note['total_chunks']} chunks"):
                st.caption(f"Pages: {note['total_pages']} | Uploaded: {note.get('uploaded_at','N/A')}")
except Exception:
    st.info("⚡ Start the backend to browse notes.")
