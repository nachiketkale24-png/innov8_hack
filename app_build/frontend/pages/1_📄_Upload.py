"""
NoteFlow AI — 📄 PDF Upload Page
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import upload_pdf, api_get, api_delete

st.set_page_config(page_title="Upload | NoteFlow AI", page_icon="📄", layout="wide")
st.title("📄 Upload PDFs")
st.markdown("Upload your study materials to build your knowledge base.")

# ── Upload ───────────────────────────────────────────────
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.info(f"📎 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("🚀 Ingest PDF", type="primary"):
        with st.spinner("Processing... extracting → chunking → indexing..."):
            try:
                result = upload_pdf(uploaded_file.name, uploaded_file.getvalue())
                st.success(f"✅ {result.get('message', 'Ingested successfully')}")
                note = result.get("note", {})
                col1, col2, col3 = st.columns(3)
                col1.metric("Pages", note.get("total_pages", "?"))
                col2.metric("Chunks", note.get("total_chunks", "?"))
                col3.metric("Title", note.get("title", "?"))
                with st.expander("📋 Full response"):
                    st.json(result)
            except Exception as e:
                st.error(f"❌ Upload failed: {e}")

# ── Existing Notes ───────────────────────────────────────
st.divider()
st.subheader("📚 Knowledge Base")

try:
    data = api_get("/api/notes")
    notes = data.get("notes", [])
    if not notes:
        st.info("No notes yet. Upload a PDF above! ☝️")
    else:
        for note in notes:
            with st.expander(f"📄 {note['title']} — {note['total_pages']} pages, {note['total_chunks']} chunks"):
                st.caption(f"File: {note['filename']} | Uploaded: {note.get('uploaded_at', 'N/A')}")
                if st.button("🗑️ Delete", key=f"del_{note['_id']}"):
                    try:
                        api_delete(f"/api/notes/{note['_id']}")
                        st.success("Deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")
except Exception:
    st.info("⚡ Start the backend to see your notes.")
