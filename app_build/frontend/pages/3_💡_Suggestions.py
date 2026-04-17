"""
NoteFlow AI — 💡 AI Suggestions Page
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import api_get, api_post

st.set_page_config(page_title="Suggestions | NoteFlow AI", page_icon="💡", layout="wide")
st.title("💡 AI Suggestions")
st.markdown("Get AI-powered summaries, simplifications, and revision questions from your notes.")

# ── Note Selector ────────────────────────────────────────
try:
    notes = api_get("/api/notes").get("notes", [])
except Exception:
    notes = []
    st.info("⚡ Start the backend to use AI suggestions.")

if not notes:
    st.warning("No notes available. Upload a PDF first!")
    st.stop()

note_map = {f"{n['title']} ({n['total_chunks']} chunks)": n["_id"] for n in notes}
selected_label = st.selectbox("Select a note:", list(note_map.keys()))
note_id = note_map[selected_label]

st.divider()

# ── Action Buttons ───────────────────────────────────────
col1, col2, col3 = st.columns(3)

action = None
if col1.button("📝 Summarize", use_container_width=True, type="primary"):
    action = ("summarize", "/api/suggest/summarize", "Summary")
if col2.button("🎯 Simplify", use_container_width=True):
    action = ("simplify", "/api/suggest/simplify", "Simplification")
if col3.button("❓ Revision Questions", use_container_width=True):
    action = ("revise", "/api/suggest/revise", "Revision Questions")

# ── Call Backend & Display ───────────────────────────────
if action:
    _, endpoint, label = action
    with st.spinner(f"Generating {label}..."):
        try:
            result = api_post(endpoint, json_data={"note_id": note_id})
            st.subheader(f"📋 {label}")
            st.markdown(result.get("content", "No content returned."))
        except Exception as e:
            st.error(f"Failed: {e}")
