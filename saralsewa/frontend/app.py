"""
SaralSewa – CivicMatch Streamlit UI (Enhanced Version)
=====================================================
Run with:
    streamlit run frontend/app.py
"""

import streamlit as st
import requests
import json
import pandas as pd

# API Configuration
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans:wght@400;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Hero Section */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        color: #1e3a8a;
        background: -webkit-linear-gradient(#1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }
    .hero-sub {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;
    }

    /* Status Badges */
    .badge-eligible {
        background: #dcfce7; color: #166534;
        padding: 6px 14px; border-radius: 50px;
        font-weight: 700; font-size: 0.75rem;
        border: 1px solid #bbf7d0;
    }
    .badge-partial {
        background: #fef9c3; color: #854d0e;
        padding: 6px 14px; border-radius: 50px;
        font-weight: 700; font-size: 0.75rem;
        border: 1px solid #fef08a;
    }
    .badge-ineligible {
        background: #fee2e2; color: #991b1b;
        padding: 6px 14px; border-radius: 50px;
        font-weight: 700; font-size: 0.75rem;
        border: 1px solid #fecaca;
    }

    /* Scheme Cards */
    .scheme-card {
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        background: #ffffff;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        transition: transform 0.2s ease;
    }
    .scheme-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }

    /* Score Bar */
    .score-bar-bg {
        background: #f1f5f9;
        border-radius: 10px;
        height: 10px;
        width: 100%;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .summary-box {
        background: #f8fafc;
        border-left: 6px solid #1e3a8a;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
    }

    .tricolor-bar {
        height: 6px;
        background: linear-gradient(90deg, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #f1f5f9;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar Configuration ─────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=80)
    st.title("User Profile")
    st.markdown("---")
    
    # Personal Info Group
    with st.expander("👤 Personal Details", expanded=True):
        name = st.text_input("Full Name", placeholder="Enter your name")
        age = st.number_input("Age", min_value=1, max_value=110, value=25)
        gender = st.selectbox("Gender", ["male", "female", "other", "prefer_not_to_say"])
    
    # Economic Info Group
    with st.expander("💰 Economic Status", expanded=True):
        income = st.number_input(
            "Annual Household Income (₹)",
            min_value=0, max_value=10000000, value=150000, step=10000
        )
        occupation = st.selectbox(
            "Primary Occupation",
            ["farmer", "self_employed", "small_business", "entrepreneur",
             "salaried", "government_employee", "unemployed", "retired", "homemaker"],
        )
        state = st.selectbox(
            "State of Residence",
            ["Andhra Pradesh", "Bihar", "Delhi", "Gujarat", "Haryana", "Karnataka", 
             "Kerala", "Maharashtra", "Punjab", "Rajasthan", "Tamil Nadu", "Uttar Pradesh", "West Bengal"]
        )

    # Document Checklist Group
    with st.expander("📄 Document Vault", expanded=True):
        st.caption("Check the documents you currently possess:")
        has_aadhaar = st.checkbox("Aadhaar Card", value=True)
        has_bank = st.checkbox("Active Bank Account", value=True)
        has_land = st.checkbox("Land Records / Patta")
        has_pan = st.checkbox("PAN Card")
        is_bpl = st.checkbox("BPL Ration Card")

    st.markdown("---")
    run_btn = st.button("🔍 Check My Eligibility", type="primary", use_container_width=True)
    
    # Sidebar Knowledge Base
    st.markdown("### 📚 Resources")
    st.info("""
    - **PM-KISAN Portal**
    - **Jan Dhan Yojana Info**
    - **Housing for All (PMAY)**
    - **MUDRA Loan Guide**
    """)

# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown('<div class="tricolor-bar"></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">SaralSewa</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Empowering citizens with AI-driven policy matching.</div>', unsafe_allow_html=True)

# ── Landing Page Logic ────────────────────────────────────────────────────────
if not run_btn:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Welcome to the Future of Governance
        SaralSewa uses the **CivicMatch Engine** to simplify the complex world of government schemes. 
        Instead of browsing thousands of pages, we map your profile against the latest 
        policy requirements in seconds.

        #### 🚀 How to get started:
        1. **Fill your profile** on the left sidebar.
        2. **Update your documents** to improve your 'Readiness Score'.
        3. **Run the Analysis** to see personalized results.
        
        ---
        #### 📈 Current Engine Coverage
        """)
        
        # Coverage Data Table
        coverage_df = pd.DataFrame({
            "Scheme Name": ["PM-KISAN", "PMJDY", "PMAY-G", "PMSBY", "PM MUDRA"],
            "Department": ["Agriculture", "Finance", "Housing", "Insurance", "MSME"],
            "Potential Benefit": ["₹6,000/year", "Insurance & Credit", "₹1.3L Grant", "₹2L Life Cover", "₹10L Loan"]
        })
        st.table(coverage_df)

    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3203/3203411.png")
        st.success("Verified by AI Governance Framework 2.0")
    
    st.stop()

# ── API Interaction Logic ─────────────────────────────────────────────────────
if not name.strip():
    st.error("⚠️ Action Required: Please enter your name in the sidebar to generate a report.")
    st.stop()

# Prepare Payload
payload = {
    "name": name.strip(),
    "age": int(age),
    "gender": gender,
    "income": int(income),
    "occupation": occupation,
    "state": state,
    "is_bpl": is_bpl,
    "has_aadhaar": has_aadhaar,
    "has_bank_account": has_bank,
    "has_land_records": has_land,
    "has_pan": has_pan,
}

with st.spinner("🧠 CivicMatch Engine is analyzing 50+ policy parameters..."):
    try:
        response = requests.post(f"{API_BASE}/match", json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ **Server Offline:** The SaralSewa Backend (FastAPI) is not reachable on port 8000.")
        st.code("uvicorn backend.main:app --reload", language="bash")
        st.stop()
    except Exception as e:
        st.error(f"❌ **Engine Error:** {str(e)}")
        st.stop()

# ── Analysis Dashboard ────────────────────────────────────────────────────────
st.balloons()

# Summary Card
st.markdown(
    f'''<div class="summary-box">
        <h3 style="margin:0;">Citizen Report: {data["user_name"]}</h3>
        <p style="margin:5px 0 0 0; color:#475569;">
            <b>Occupation:</b> {occupation.replace("_", " ").title()} | 
            <b>Location:</b> {state} | 
            <b>Annual Income:</b> ₹{income:,}
        </p>
    </div>''',
    unsafe_allow_html=True
)

# Statistics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Analyzed", data["total_schemes_checked"])
m2.metric("Eligible", data["eligible_count"], delta=f"{data['eligible_count']} schemes")
m3.metric("Partially Ready", data["partially_eligible_count"], delta_color="off")
m4.metric("Ineligible", data["ineligible_count"], delta="-", delta_color="inverse")

# Top Recommendation Highlight
if data.get("top_recommendation"):
    st.warning(f"🎯 **AI Priority Match:** Based on your profile, your best fit is **{data['top_recommendation']}**.")

st.markdown("---")

# ── Results Filtering & Listing ────────────────────────────────────────────────
res_col, filter_col = st.columns([3, 1])
with res_col:
    st.subheader("📋 Personalized Policy Matches")
with filter_col:
    filter_mode = st.selectbox(
        "View Mode",
        ["All Matches", "Eligible Only", "High Readiness (>70%)", "Action Required"],
        label_visibility="collapsed"
    )

# Filter logic
results = data["results"]
if filter_mode == "Eligible Only":
    results = [r for r in results if r["is_eligible"]]
elif filter_mode == "High Readiness (>70%)":
    results = [r for r in results if r["readiness_score"] > 70]
elif filter_mode == "Action Required":
    results = [r for r in results if len(r["missing_documents"]) > 0]

# ── Render Scheme Cards ───────────────────────────────────────────────────────
for r in results:
    score = r["readiness_score"]
    
    # Determine UI Colors
    if r["is_eligible"] and score >= 80:
        status_badge = '<span class="badge-eligible">✅ FULLY ELIGIBLE</span>'
        border_color = "#166534"
        bar_color = "#22c55e"
    elif r["is_eligible"]:
        status_badge = '<span class="badge-partial">🟡 PARTIAL READINESS</span>'
        border_color = "#854d0e"
        bar_color = "#eab308"
    else:
        status_badge = '<span class="badge-ineligible">❌ NOT ELIGIBLE</span>'
        border_color = "#991b1b"
        bar_color = "#ef4444"

    # HTML Card Generation
    st.markdown(f"""
    <div class="scheme-card" style="border-left: 5px solid {border_color};">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:1.2rem; font-weight:700; color:#1e293b;">
                #{r["relevance_rank"]} {r["scheme_name"]}
                <span style="font-size:0.8rem; color:#64748b; font-weight:400; margin-left:10px;">{r["category"]}</span>
            </div>
            {status_badge}
        </div>
        <div style="margin: 10px 0; color:#334155;">
            <b>Primary Benefit:</b> {r["benefit"]}
        </div>
        <div style="font-size:0.85rem; color:#64748b; margin-top:15px;">
            Application Readiness: <b>{score}%</b>
        </div>
        <div class="score-bar-bg">
            <div style="width:{score}%; height:100%; background:{bar_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Detailed Expander
    with st.expander(f"Detailed Analysis & Next Steps for {r['scheme_name']}"):
        t1, t2, t3, t4 = st.tabs(["Eligibility Reasons", "Document Gaps", "Conditional Gaps", "Execution Plan"])
        
        with t1:
            if r["eligibility_reasons"]:
                st.markdown("**Why you qualify:**")
                for reason in r["eligibility_reasons"]:
                    st.write(f"✅ {reason}")
            if r["ineligibility_reasons"]:
                st.markdown("**Why you don't qualify yet:**")
                for reason in r["ineligibility_reasons"]:
                    st.write(f"🛑 {reason}")
        
        with t2:
            if r["missing_documents"]:
                st.error("The following documents are mandatory but missing:")
                for doc in r["missing_documents"]:
                    st.write(f"📝 {doc}")
            else:
                st.success("Documentation Complete! You have all required files.")

        with t3:
            if r["missing_conditions"]:
                st.warning("Social/Physical conditions to address:")
                for cond in r["missing_conditions"]:
                    st.write(f"⚠️ {cond}")
            else:
                st.write("No additional demographic conditions found.")

        with t4:
            st.markdown("#### Roadmap to Benefit")
            for i, step in enumerate(r["action_steps"]):
                st.info(f"Step {i+1}: {step}")

# ── Final Footer ──────────────────────────────────────────────────────────────
st.markdown("---")
f_col1, f_col2 = st.columns([3, 1])
with f_col1:
    st.caption("© 2026 SaralSewa AI Governance Framework. Powered by CivicMatch Core v2.4.5.")
    st.caption("Disclaimer: This tool provides estimations based on public policy data. Verify at Seva Sindhu or MyScheme portals.")
with f_col2:
    if st.button("📥 Download Report (PDF)"):
        st.toast("Generating PDF... this will take a moment.")