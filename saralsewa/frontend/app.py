"""
SaralSewa – CivicMatch Streamlit UI
=====================================
Run with:
    streamlit run frontend/app.py
"""

import streamlit as st
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SaralSewa – AI Governance Copilot",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&family=Tiro+Devanagari+Hindi&display=swap');

    html, body, [class*="css"] { font-family: 'Noto Sans', sans-serif; }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 700;
        color: #0f3460;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        font-size: 1.1rem;
        color: #555;
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
    }
    .badge-eligible {
        background: #d4edda; color: #155724;
        padding: 4px 12px; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem;
    }
    .badge-partial {
        background: #fff3cd; color: #856404;
        padding: 4px 12px; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem;
    }
    .badge-ineligible {
        background: #f8d7da; color: #721c24;
        padding: 4px 12px; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem;
    }
    .scheme-card {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        background: #ffffff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .score-bar-bg {
        background: #e9ecef;
        border-radius: 8px;
        height: 12px;
        width: 100%;
        margin: 6px 0 2px 0;
    }
    .summary-box {
        background: linear-gradient(135deg, #e8f4f8 0%, #f0f9f0 100%);
        border-left: 4px solid #0f3460;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .tricolor-bar {
        height: 5px;
        background: linear-gradient(90deg, #FF9933 33%, #FFFFFF 33%, #FFFFFF 66%, #138808 66%);
        border-radius: 3px;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="tricolor-bar"></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">🇮🇳 SaralSewa</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">AI Governance Copilot · CivicMatch – Eligibility & Readiness Engine</div>',
    unsafe_allow_html=True,
)

# ── Sidebar inputs ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📋 Your Profile")
    st.caption("Fill in your details to check scheme eligibility")

    name = st.text_input("Full Name", placeholder="e.g. Ramesh Kumar")
    age = st.number_input("Age", min_value=1, max_value=100, value=30, step=1)
    gender = st.selectbox("Gender", ["male", "female", "other"])
    income = st.number_input(
        "Annual Household Income (₹)",
        min_value=0, max_value=5000000, value=120000, step=5000,
        help="Enter your approximate annual family income in INR"
    )
    occupation = st.selectbox(
        "Occupation",
        ["farmer", "self_employed", "small_business", "entrepreneur",
         "salaried", "government_employee", "unemployed", "retired", "homemaker"],
    )
    state = st.text_input("State", value="Maharashtra", placeholder="e.g. Rajasthan")

    st.markdown("---")
    st.subheader("📄 Documents Available")
    has_aadhaar = st.checkbox("Aadhaar Card", value=True)
    has_bank = st.checkbox("Bank Account", value=True)
    has_land = st.checkbox("Land Records / Khasra")
    has_pan = st.checkbox("PAN Card")
    is_bpl = st.checkbox("BPL Ration Card")

    st.markdown("---")
    run_btn = st.button("🔍 Check My Eligibility", type="primary", use_container_width=True)

# ── Main content ──────────────────────────────────────────────────────────────
if not run_btn:
    st.info(
        "👈 Fill in your profile on the left and click **Check My Eligibility** to get started.",
        icon="ℹ️",
    )
    st.markdown("""
    ### How it works
    1. **Enter your details** in the sidebar (age, income, occupation, etc.)
    2. **Tick the documents** you already have
    3. Click **Check My Eligibility**
    4. Get instant eligibility results with **readiness scores** and **action steps**

    ---
    #### Schemes covered in this MVP
    | Scheme | Category | Benefit |
    |---|---|---|
    | PM-KISAN | Agriculture | ₹6,000/year |
    | PMJDY | Financial Inclusion | Zero-balance account + ₹2L insurance |
    | PMAY-G | Housing | Up to ₹1.3L for house construction |
    | PMSBY | Insurance | ₹2L accident cover @ ₹20/year |
    | PM MUDRA | Entrepreneurship | Loans up to ₹10L |
    """)
    st.stop()

# ── Validate name ─────────────────────────────────────────────────────────────
if not name.strip():
    st.warning("Please enter your name in the sidebar before proceeding.")
    st.stop()

# ── Build API payload ─────────────────────────────────────────────────────────
payload = {
    "name": name.strip(),
    "age": int(age),
    "gender": gender,
    "income": int(income),
    "occupation": occupation,
    "state": state.strip() or "Unknown",
    "is_bpl": is_bpl,
    "has_aadhaar": has_aadhaar,
    "has_bank_account": has_bank,
    "has_land_records": has_land,
    "has_pan": has_pan,
}

# ── Call API ──────────────────────────────────────────────────────────────────
with st.spinner("Analyzing your eligibility across all schemes..."):
    try:
        resp = requests.post(f"{API_BASE}/match", json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        st.error(
            "❌ Cannot connect to the API server. "
            "Please make sure the FastAPI backend is running on port 8000.\n\n"
            "```bash\nuvicorn backend.main:app --reload\n```"
        )
        st.stop()
    except Exception as e:
        st.error(f"API Error: {e}")
        st.stop()

# ── Summary metrics ───────────────────────────────────────────────────────────
st.markdown(
    f'<div class="summary-box">'
    f'<b>👤 {data["user_name"]}</b> — {payload["occupation"].replace("_", " ").title()} | '
    f'Age {payload["age"]} | Income ₹{payload["income"]:,} | {payload["state"]}'
    f"</div>",
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Schemes Checked", data["total_schemes_checked"])
col2.metric("✅ Eligible", data["eligible_count"])
col3.metric("🟡 Partially Eligible", data["partially_eligible_count"])
col4.metric("❌ Not Eligible", data["ineligible_count"])

if data.get("top_recommendation"):
    st.success(f"🏆 Top Recommendation: **{data['top_recommendation']}**")

st.markdown("---")

# ── Filter options ────────────────────────────────────────────────────────────
filter_col1, filter_col2 = st.columns([2, 1])
with filter_col1:
    st.subheader("📊 Scheme Results (Ranked by Relevance)")
with filter_col2:
    show_filter = st.selectbox(
        "Filter",
        ["All", "Eligible Only", "Not Eligible"],
        label_visibility="collapsed",
    )

results = data["results"]
if show_filter == "Eligible Only":
    results = [r for r in results if r["is_eligible"]]
elif show_filter == "Not Eligible":
    results = [r for r in results if not r["is_eligible"]]

# ── Render each scheme card ───────────────────────────────────────────────────
for r in results:
    score = r["readiness_score"]

    if r["is_eligible"] and score >= 80:
        badge = '<span class="badge-eligible">✅ ELIGIBLE</span>'
        border_color = "#28a745"
    elif r["is_eligible"]:
        badge = '<span class="badge-partial">🟡 PARTIALLY READY</span>'
        border_color = "#ffc107"
    else:
        badge = '<span class="badge-ineligible">❌ NOT ELIGIBLE</span>'
        border_color = "#dc3545"

    # Score bar
    bar_color = "#28a745" if score >= 70 else ("#ffc107" if score >= 40 else "#dc3545")
    score_bar = f"""
    <div class="score-bar-bg">
      <div style="width:{score}%; height:100%; background:{bar_color}; border-radius:8px; transition:width 0.6s;"></div>
    </div>
    """

    st.markdown(
        f'<div class="scheme-card" style="border-left: 4px solid {border_color};">'
        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
        f'<div><b style="font-size:1.05rem;">#{r["relevance_rank"]} {r["scheme_name"]}</b>'
        f' &nbsp; <span style="color:#888; font-size:0.85rem;">{r["category"]}</span></div>'
        f'{badge}</div>'
        f'<div style="color:#333; margin:6px 0; font-size:0.92rem;">💰 {r["benefit"]}</div>'
        f'<div style="font-size:0.88rem; color:#555; margin-bottom:4px;">Readiness Score: <b>{score}%</b></div>'
        f'{score_bar}'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.expander(f"View Details — {r['scheme_name']}"):
        tab1, tab2, tab3, tab4 = st.tabs(
            ["✅ Eligibility Check", "📄 Documents", "⚠️ Gaps & Conditions", "🪜 Action Steps"]
        )

        with tab1:
            if r["eligibility_reasons"]:
                st.markdown("**Criteria Met:**")
                for reason in r["eligibility_reasons"]:
                    st.markdown(f"- ✅ {reason}")
            if r["ineligibility_reasons"]:
                st.markdown("**Criteria Not Met:**")
                for reason in r["ineligibility_reasons"]:
                    st.markdown(f"- ❌ {reason}")

        with tab2:
            if r["missing_documents"]:
                st.error("Missing Documents:")
                for doc in r["missing_documents"]:
                    st.markdown(f"- 📌 {doc}")
            else:
                st.success("All required documents are available! ✅")

        with tab3:
            if r["missing_conditions"]:
                st.warning("Address these gaps:")
                for cond in r["missing_conditions"]:
                    st.markdown(f"- ⚠️ {cond}")
            else:
                st.success("No additional conditions to meet!")

        with tab4:
            for step in r["action_steps"]:
                st.markdown(step)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "SaralSewa MVP · CivicMatch Core · Data is for demo purposes. "
    "Always verify eligibility with official government portals."
)