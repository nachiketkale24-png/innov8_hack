"""
SaralSewa – CivicMatch Streamlit UI (Fixed + Enhanced v2.0)
============================================================
Fixes applied:
  1. Removed broken `from utils import ...` in backend main.py
  2. Added correct path for frontend utils import
  3. Fixed `use_column_width` deprecation warning → `use_container_width`
  4. Added Marathi language support
  5. Added category filter in sidebar
  6. Added scheme search/filter in results
  7. Added ministry info and tags in scheme cards
  8. Added summary text in scheme cards
  9. Fixed session state reset on new search
  10. Added proper error details display
  11. Added average readiness score metric
  12. Added PDF-style text report download
"""

import sys
import os

# FIX: Ensure frontend utils (not backend) is imported
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import (
    generate_suggestions,
    get_localized_strings,
    format_income,
    get_score_color,
    get_category_icon,
)

# ── API CONFIGURATION ────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api/v1"

# ── SESSION STATE INITIALIZATION ──────────────────────────────────────────────
for key, default in [
    ("language", "EN"),
    ("report_generated", False),
    ("api_data", None),
    ("last_payload", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── PAGE CONFIGURATION ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="SaralSewa | AI Governance",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── ADVANCED CUSTOM CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    .hero-sub {
        font-size: 1.1rem;
        color: #64748b;
        margin-top: 4px;
        margin-bottom: 20px;
    }

    .scheme-card {
        background: white;
        padding: 2rem;
        border-radius: 18px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .scheme-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }

    .status-badge {
        padding: 5px 15px;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    .eligible-badge { background-color: #dcfce7; color: #166534; }
    .ineligible-badge { background-color: #fee2e2; color: #991b1b; }
    .partial-badge { background-color: #fef9c3; color: #854d0e; }

    .custom-progress-bg {
        background-color: #f1f5f9;
        border-radius: 10px;
        height: 8px;
        width: 100%;
        margin-top: 10px;
    }
    .custom-progress-fill {
        height: 100%;
        border-radius: 10px;
    }

    .summary-stats {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }

    .tricolor-header {
        height: 8px;
        background: linear-gradient(90deg, #FF9933 33.33%, #FFFFFF 33.33%, #FFFFFF 66.66%, #138808 66.66%);
        border-radius: 4px;
        margin-bottom: 25px;
    }

    .tag-pill {
        display: inline-block;
        padding: 2px 10px;
        background-color: #eff6ff;
        color: #1d4ed8;
        border-radius: 20px;
        font-size: 0.7rem;
        margin: 2px;
        font-weight: 600;
    }

    .summary-text {
        font-size: 0.9rem;
        color: #475569;
        font-style: italic;
        margin: 10px 0;
        padding: 10px;
        background: #f8fafc;
        border-left: 3px solid #3b82f6;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── UI TEXT LOCALIZATION ──────────────────────────────────────────────────────
strings = get_localized_strings(st.session_state.language)

# ── SIDEBAR INTERFACE ─────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=70)
    except Exception:
        st.markdown("🇮🇳")
    
    st.title(strings["sidebar_header"])

    # FIX: Added Marathi as 3rd language option
    st.session_state.language = st.radio(
        "Select Language / भाषा चुनें / भाषा निवडा",
        ["EN", "HI", "MR"],
        horizontal=True
    )
    strings = get_localized_strings(st.session_state.language)

    st.markdown("---")

    with st.container():
        st.subheader("👤 Profile Information")
        name = st.text_input("Full Name", placeholder="e.g. Ramesh Kumar")
        age = st.number_input("Age", min_value=1, max_value=115, value=30)
        gender = st.selectbox("Gender", ["male", "female", "other", "prefer_not_to_say"])

    with st.container():
        st.subheader("💰 Socio-Economic Data")
        income = st.number_input(
            "Annual Household Income (Rs.)",
            min_value=0, step=10000, value=120000,
            help="Enter your total annual household income in Indian Rupees"
        )
        st.caption(f"That's approximately {format_income(income)}")

        occupation = st.selectbox(
            "Primary Occupation",
            ["farmer", "self_employed", "salaried", "unemployed", "retired", "small_business", "entrepreneur", "homemaker"]
        )
        state = st.selectbox(
            "State of Residence",
            sorted([
                "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
                "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
                "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
                "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
                "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
                "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi",
                "Jammu & Kashmir", "Ladakh"
            ])
        )

    with st.container():
        st.subheader("📄 Document Checklist")
        st.caption("Which documents do you currently hold?")
        col_a, col_b = st.columns(2)
        with col_a:
            has_aadhaar = st.checkbox("Aadhaar", value=True)
            has_bank = st.checkbox("Bank A/c", value=True)
        with col_b:
            has_pan = st.checkbox("PAN Card")
            is_bpl = st.checkbox("BPL Card")
        has_land = st.checkbox("Land Records (Khasra/Khatauni)")

    # FIX: Added category filter
    with st.container():
        st.subheader("🔍 Filter Options")
        category_options = [
            "All Categories", "Agriculture", "Financial Inclusion", "Housing",
            "Insurance", "Entrepreneurship", "Pension", "Education",
            "Skill Development", "Women & Child", "Food Security",
            "Energy & Welfare", "Urban Livelihood", "Employment"
        ]
        selected_category = st.selectbox("Filter by Category", category_options)

    st.markdown("---")
    analyze_btn = st.button(strings["check_btn"], type="primary", use_container_width=True)

    # FIX: Added reset button
    if st.session_state.report_generated:
        if st.button("🔄 New Search", use_container_width=True):
            st.session_state.report_generated = False
            st.session_state.api_data = None
            st.rerun()

    with st.expander("🛠 Help & Documentation"):
        st.write("**How we calculate eligibility?**")
        st.info(
            "Our engine checks age, income, occupation, gender, state, BPL status, "
            "and required documents against each scheme's official criteria. "
            "The readiness score weighs rule compliance (60%) and document availability (40%)."
        )
        st.write("**Data Sources:** Government Gazettes, Ministry websites, and official portals.")

# ── MAIN CONTENT AREA ─────────────────────────────────────────────────────────
st.markdown('<div class="tricolor-header"></div>', unsafe_allow_html=True)
st.markdown(f'<h1 class="hero-title">{strings["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="hero-sub">{strings["hero_sub"]}</p>', unsafe_allow_html=True)

# ── LANDING PAGE VIEW ────────────────────────────────────────────────────────
if not analyze_btn and not st.session_state.report_generated:
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.markdown("""
        ### Why use SaralSewa?
        Navigating government bureaucracy in India is complex. Millions of citizens miss out on 
        benefits simply because they don't know they qualify.
        
        **Our Platform Provides:**
        - **Instant Audit:** Cross-reference 15 schemes in 2 seconds.
        - **Readiness Score:** Know exactly how 'ready' your paperwork is.
        - **Actionable Roadmap:** Step-by-step guide to applying.
        - **Multi-language Support:** English, Hindi & Marathi.
        
        ---
        #### Scheme Categories Covered
        """)

        cat_cols = st.columns(4)
        cat_cols[0].metric("Agriculture", "3 Schemes")
        cat_cols[1].metric("Insurance", "3 Schemes")
        cat_cols[2].metric("Education", "2 Schemes")
        cat_cols[3].metric("Housing", "1 Scheme")
        
        cat_cols2 = st.columns(4)
        cat_cols2[0].metric("Livelihood", "3 Schemes")
        cat_cols2[1].metric("Finance", "2 Schemes")
        cat_cols2[2].metric("Women", "2 Schemes")
        cat_cols2[3].metric("Food", "1 Scheme")

    with col2:
        st.markdown("### 📈 Scheme Distribution")
        fig = px.pie(
            values=[3, 3, 2, 1, 3, 2, 2, 1],
            names=["Agriculture", "Insurance", "Education", "Housing",
                   "Livelihood", "Finance", "Women/Child", "Food"],
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)   # FIX: use_container_width not use_column_width

        st.success("✅ 15 Schemes Loaded & Ready")
        st.warning("⚠️ Keep your Aadhaar ready for maximum accuracy.")

    st.stop()

# ── API INTEGRATION & LOADING ────────────────────────────────────────────────
if analyze_btn:
    if not name or len(name.strip()) < 2:
        st.error("❌ Please enter your full name (minimum 2 characters) in the sidebar.")
        st.stop()

    payload = {
        "name": name.strip(),
        "age": age,
        "gender": gender,
        "income": income,
        "occupation": occupation,
        "state": state,
        "is_bpl": is_bpl,
        "has_aadhaar": has_aadhaar,
        "has_bank_account": has_bank,
        "has_land_records": has_land,
        "has_pan": has_pan,
        "category_filter": None if selected_category == "All Categories" else selected_category,
    }

    with st.spinner(strings["loading"]):
        try:
            response = requests.post("http://localhost:8000/api/v1/match", json=payload)
            data = response.json()
            st.session_state.api_data = data
            st.session_state.last_payload = payload
            st.session_state.report_generated = True
        except requests.exceptions.ConnectionError:
            st.error(
                "⚠️ **Backend Offline**: Cannot connect to CivicMatch Backend at `localhost:8000`.\n\n"
                "**To start the backend:**\n"
                "```bash\ncd saralsewa\nuvicorn backend.main:app --reload\n```"
            )
            st.stop()
        except requests.exceptions.HTTPError as e:
            # FIX: Show detailed error from FastAPI
            try:
                err_detail = response.json().get("detail", str(e))
            except Exception:
                err_detail = str(e)
            st.error(f"⚠️ **API Error ({response.status_code}):** {err_detail}")
            st.stop()
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {str(e)}")
            st.stop()

# ── ANALYSIS DASHBOARD ────────────────────────────────────────────────────────
if st.session_state.report_generated and st.session_state.api_data:
    data = st.session_state.api_data

    # ── Header Metrics ──
    avg_score = data.get("average_readiness_score", 0)
    st.markdown(f"""
    <div class="summary-stats">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
            <div>
                <h2 style="margin:0; color:white;">Analysis for {data['user_name']}</h2>
                <p style="margin:0; opacity:0.8;">Generated on {datetime.now().strftime('%d %b %Y, %H:%M')}</p>
            </div>
            <div style="display:flex; gap:2rem; text-align:center;">
                <div>
                    <span style="font-size:2rem; font-weight:800; color:#86efac;">{data['eligible_count']}</span><br/>
                    <span style="opacity:0.8; font-size:0.85rem;">Eligible</span>
                </div>
                <div>
                    <span style="font-size:2rem; font-weight:800; color:#fde68a;">{data['partially_eligible_count']}</span><br/>
                    <span style="opacity:0.8; font-size:0.85rem;">Partial</span>
                </div>
                <div>
                    <span style="font-size:2rem; font-weight:800; color:#fca5a5;">{data['ineligible_count']}</span><br/>
                    <span style="opacity:0.8; font-size:0.85rem;">Ineligible</span>
                </div>
                <div>
                    <span style="font-size:2rem; font-weight:800; color:#a5f3fc;">{avg_score}%</span><br/>
                    <span style="opacity:0.8; font-size:0.85rem;">Avg. Readiness</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top Recommendation & AI Suggestions ──
    top_col, sug_col = st.columns([1, 1])

    with top_col:
        st.markdown(f"### 🎯 {strings['top_rec_label']}")
        if data.get("top_recommendation"):
            st.success(f"**{data['top_recommendation']}**")
            st.info(
                f"👉 Based on your profile as a **{st.session_state.last_payload.get('occupation', 'citizen')}** "
                f"from **{st.session_state.last_payload.get('state', 'India')}**, "
                f"this scheme offers the highest benefit-to-effort ratio."
            )
        else:
            st.info("No perfect match found. Check partial matches below.")

    with sug_col:
        st.markdown(f"### 🤖 {strings['suggestions_label']}")
        suggestions = generate_suggestions(data["results"])
        if suggestions:
            for s in suggestions[:3]:
                st.warning(s)
        else:
            st.success("✅ You are document-ready for all eligible schemes!")

    st.divider()

    # ── Results Visualization ──
    tab_list, tab_viz, tab_summary = st.tabs([
        "📋 Detailed Matches",
        "📊 Readiness Analytics",
        "📝 Text Summary"
    ])

    with tab_list:
        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        with f_col2:
            sort_opt = st.selectbox("Sort By", ["Readiness Score", "Relevance Rank", "Category"])
        with f_col3:
            # FIX: Added filter by eligibility status
            filter_status = st.selectbox("Show", ["All", "Eligible Only", "Not Eligible"])

        results_to_show = data["results"]
        if filter_status == "Eligible Only":
            results_to_show = [r for r in results_to_show if r["is_eligible"]]
        elif filter_status == "Not Eligible":
            results_to_show = [r for r in results_to_show if not r["is_eligible"]]

        if sort_opt == "Readiness Score":
            results_to_show = sorted(results_to_show, key=lambda r: r["readiness_score"], reverse=True)
        elif sort_opt == "Category":
            results_to_show = sorted(results_to_show, key=lambda r: r["category"])

        if not results_to_show:
            st.info("No results match your filter. Try adjusting the filter above.")

        for res in results_to_show:
            score = res["readiness_score"]
            score_color = get_score_color(score)
            category_icon = get_category_icon(res.get("category", ""))

            if res["is_eligible"] and score >= 80:
                badge_class = "eligible-badge"
                badge_text = strings["eligible_label"]
            elif res["is_eligible"]:
                badge_class = "partial-badge"
                badge_text = strings["partial_label"]
            else:
                badge_class = "ineligible-badge"
                badge_text = strings["not_eligible_label"]

            # FIX: Render tags
            tags_html = "".join(
                f'<span class="tag-pill">{tag}</span>'
                for tag in res.get("tags", [])[:5]
            )

            # FIX: Render summary
            summary_html = ""
            if res.get("summary"):
                summary_html = f'<div class="summary-text">{res["summary"]}</div>'

            st.markdown(f"""
            <div class="scheme-card">
                <div style="display:flex; justify-content:space-between; align-items:start; flex-wrap:wrap; gap:1rem;">
                    <div style="flex:1;">
                        <span class="status-badge {badge_class}">{badge_text}</span>
                        <h3 style="margin:10px 0 5px 0;">{category_icon} {res['scheme_name']}</h3>
                        <p style="color:#64748b; font-size:0.85rem; margin:0;">
                            {res.get('ministry', 'Government of India')} · {res['category']}
                        </p>
                        <div style="margin-top:8px;">{tags_html}</div>
                    </div>
                    <div style="text-align:right; min-width:80px;">
                        <span style="font-size:1.6rem; font-weight:800; color:{score_color};">{score}%</span><br/>
                        <small style="color:#94a3b8;">{strings['readiness_label']}</small><br/>
                        <small style="color:#94a3b8;">Rank #{res.get('relevance_rank', '?')}</small>
                    </div>
                </div>
                {summary_html}
                <div style="margin: 15px 0;">
                    <b>Benefit:</b> {res['benefit']}
                </div>
                <div class="custom-progress-bg">
                    <div class="custom-progress-fill" style="width: {score}%; background: {score_color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("🔍 View Action Plan & Gaps"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Eligibility Check:**")
                    for reason in res["eligibility_reasons"]:
                        st.write(f"✅ {reason}")
                    for reason in res["ineligibility_reasons"]:
                        st.write(f"❌ {reason}")
                    if res.get("missing_documents"):
                        st.markdown("**Missing Documents:**")
                        for doc in res["missing_documents"]:
                            st.write(f"📄 {doc}")
                with c2:
                    st.markdown("**Required Steps:**")
                    for step in res["action_steps"]:
                        if step.startswith("  "):
                            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{step.strip()}")
                        else:
                            st.write(f"🔹 {step}")

    with tab_viz:
        st.markdown("#### Readiness Score Comparison")
        chart_data = pd.DataFrame([
            {
                "Scheme": r["scheme_name"][:30] + "..." if len(r["scheme_name"]) > 30 else r["scheme_name"],
                "Score": r["readiness_score"],
                "Status": "Eligible" if r["is_eligible"] else "Not Eligible",
                "Category": r.get("category", "Other"),
            }
            for r in data["results"]
        ])

        fig_bar = px.bar(
            chart_data,
            x="Score",
            y="Scheme",
            orientation='h',
            color="Status",
            color_discrete_map={"Eligible": "#16a34a", "Not Eligible": "#dc2626"},
            hover_data=["Category"],
            title="Readiness Scores by Scheme"
        )
        fig_bar.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

        # FIX: Added category breakdown chart
        st.markdown("#### Category Distribution")
        cat_data = chart_data.groupby("Category")["Score"].mean().reset_index()
        fig_cat = px.bar(
            cat_data, x="Category", y="Score",
            color="Score", color_continuous_scale="Blues",
            title="Average Readiness by Category"
        )
        fig_cat.update_layout(height=300)
        st.plotly_chart(fig_cat, use_container_width=True)

    with tab_summary:
        # FIX: New tab with plain text summary for printing/sharing
        st.markdown("#### Plain Text Summary Report")
        
        summary_lines = [
            f"SARALSEWA ELIGIBILITY REPORT",
            f"{'='*50}",
            f"Citizen: {data['user_name']}",
            f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}",
            f"Schemes Checked: {data['total_schemes_checked']}",
            f"Eligible: {data['eligible_count']} | Partial: {data['partially_eligible_count']} | Ineligible: {data['ineligible_count']}",
            f"Average Readiness: {avg_score}%",
            f"Top Recommendation: {data.get('top_recommendation', 'N/A')}",
            f"",
            f"{'='*50}",
            f"ELIGIBLE SCHEMES:",
            f"{'='*50}",
        ]
        for r in data["results"]:
            if r["is_eligible"]:
                summary_lines.append(f"\n✅ {r['scheme_name']}")
                summary_lines.append(f"   Readiness: {r['readiness_score']}% | Category: {r['category']}")
                summary_lines.append(f"   Benefit: {r['benefit']}")
                if r.get("missing_documents"):
                    summary_lines.append(f"   Missing Docs: {', '.join(r['missing_documents'])}")

        summary_lines += [f"", f"{'='*50}", f"NOT ELIGIBLE SCHEMES:", f"{'='*50}"]
        for r in data["results"]:
            if not r["is_eligible"]:
                summary_lines.append(f"\n❌ {r['scheme_name']} (Score: {r['readiness_score']}%)")
                if r.get("ineligibility_reasons"):
                    summary_lines.append(f"   Reason: {r['ineligibility_reasons'][0]}")

        summary_text = "\n".join(summary_lines)
        st.text_area("Full Report", summary_text, height=400)

    # ── REPORT EXPORT ──
    st.markdown("---")
    st.subheader(f"📥 {strings['export_label']}")

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    json_str = json.dumps(data, indent=2)
    exp_col1.download_button(
        label="⬇️ Download JSON Report",
        data=json_str,
        file_name=f"SaralSewa_Report_{name}_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )

    df_export = pd.DataFrame(data["results"])
    # FIX: Flatten list columns for clean CSV
    for col in ["eligibility_reasons", "ineligibility_reasons", "missing_documents", "action_steps", "tags"]:
        if col in df_export.columns:
            df_export[col] = df_export[col].apply(lambda x: " | ".join(x) if isinstance(x, list) else x)
    csv_data = df_export.to_csv(index=False).encode('utf-8')
    exp_col2.download_button(
        label="⬇️ Download CSV Table",
        data=csv_data,
        file_name=f"SaralSewa_Summary_{name}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    # FIX: Text report download instead of broken print button
    exp_col3.download_button(
        label="⬇️ Download Text Report",
        data=summary_text if st.session_state.report_generated else "",
        file_name=f"SaralSewa_TextReport_{name}_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br/><br/>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#94a3b8; border-top:1px solid #e2e8f0; padding-top:20px;">
    <p>SaralSewa CivicMatch Engine v2.0.0 | 🇮🇳 Digital India Initiative</p>
    <p style="font-size:0.7rem;">
        Disclaimer: This AI tool provides guidance based on available digital data. 
        Always verify with the official Seva Kendra or Department Portal before financial commitments.
    </p>
</div>
""", unsafe_allow_html=True)

# ── DEV MODE ──────────────────────────────────────────────────────────────────
if st.sidebar.checkbox("⚙️ Dev Mode"):
    st.sidebar.divider()
    st.sidebar.subheader("System Status")
    st.sidebar.write(f"Language: {st.session_state.language}")
    st.sidebar.write(f"API Base: {API_BASE}")
    st.sidebar.write(f"Report generated: {st.session_state.report_generated}")
    if st.session_state.last_payload:
        st.sidebar.json(st.session_state.last_payload)