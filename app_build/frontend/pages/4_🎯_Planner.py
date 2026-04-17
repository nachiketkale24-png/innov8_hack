"""
NoteFlow AI — 🎯 Learning Planner Page
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from utils import api_post, api_get

st.set_page_config(page_title="Planner | NoteFlow AI", page_icon="🎯", layout="wide")
st.title("🎯 Learning Planner")
st.markdown("Set a goal and get a structured study roadmap powered by AI.")

# ── Goal Form ────────────────────────────────────────────
goal = st.text_input("What do you want to learn?", placeholder="e.g., Master Neural Networks in 2 weeks")
timeframe = st.selectbox("Timeframe", ["1 week", "2 weeks", "1 month", "flexible"], index=3)

if st.button("🚀 Generate Plan", type="primary") and goal.strip():
    with st.spinner("AI is building your roadmap..."):
        try:
            result = api_post("/api/planner/create", json_data={"goal": goal.strip(), "timeframe": timeframe})
            plan = result.get("plan", {})
            st.success("✅ Plan created!")
            st.subheader(f"📋 Roadmap: {plan.get('goal', goal)}")

            roadmap = plan.get("roadmap", [])
            if not roadmap:
                st.warning("No roadmap data returned.")
            for week in roadmap:
                with st.expander(
                    f"📅 Week {week.get('week','?')}: {week.get('title','')}",
                    expanded=True,
                ):
                    for task in week.get("tasks", []):
                        st.markdown(f"- {task}")
                    linked = week.get("linked_note_ids", [])
                    if linked:
                        st.caption(f"📎 Notes: {', '.join(linked)}")
        except Exception as e:
            st.error(f"Plan creation failed: {e}")

# ── Saved Plans ──────────────────────────────────────────
st.divider()
st.subheader("📂 Saved Plans")

try:
    plans = api_get("/api/planner").get("plans", [])
    if not plans:
        st.info("No plans yet. Enter a goal above! ☝️")
    else:
        for plan in plans:
            with st.expander(f"🎯 {plan['goal']} — {plan.get('created_at','')[:10]}"):
                for week in plan.get("roadmap", []):
                    st.markdown(f"**Week {week.get('week','?')}: {week.get('title','')}**")
                    for task in week.get("tasks", []):
                        st.markdown(f"  - {task}")
except Exception:
    st.info("⚡ Start the backend to see saved plans.")
