"""
NoteFlow AI — 📊 Dashboard & Understanding Score Page
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import api_get

st.set_page_config(page_title="Dashboard | NoteFlow AI", page_icon="📊", layout="wide")
st.title("📊 Dashboard")
st.markdown("Track your learning engagement and Understanding Score.")

# ── Understanding Score ──────────────────────────────────
try:
    score_data = api_get("/api/score")
    score = score_data.get("score", 0)
    bd = score_data.get("breakdown", {})

    st.subheader("🧠 Understanding Score")
    st.progress(score / 100)
    st.markdown(f"## **{score} / 100**")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 Notes", bd.get("notes_uploaded", 0), help="+5 pts each")
    col2.metric("🔍 Searches", bd.get("queries_made", 0), help="+3 pts each")
    col3.metric("💡 Suggestions", bd.get("suggestions_used", 0), help="+4 pts each")
    col4.metric("🎯 Plans", bd.get("planner_interactions", 0), help="+8 pts each")
    st.caption(f"Raw score: {bd.get('raw_score', 0)} → capped at 100")

except Exception as e:
    st.error(f"Could not load score: {e}")

# ── Recent Activity ──────────────────────────────────────
st.divider()
st.subheader("📜 Recent Activity")

ICONS = {
    "pdf_upload": "📄",
    "search": "🔍",
    "summarize": "📝",
    "simplify": "🎯",
    "revise": "❓",
    "plan_create": "🗺️",
}

try:
    activities = api_get("/api/activity").get("activity", [])
    if not activities:
        st.info("No activity yet. Start uploading and exploring!")
    else:
        for a in activities:
            icon = ICONS.get(a.get("action", ""), "📌")
            ts = str(a.get("timestamp", ""))[:19].replace("T", " ")
            st.markdown(f"{icon} **{a.get('action','')}** — {a.get('details','')}")
            st.caption(f"🕐 {ts}")
except Exception as e:
    st.error(f"Could not load activity: {e}")
