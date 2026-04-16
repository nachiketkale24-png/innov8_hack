import React, { useState } from "react";
import "./App.css";

const STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
  "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
  "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
  "Uttarakhand","West Bengal","Delhi","Jammu & Kashmir","Ladakh",
];

const OCCUPATIONS = ["student","farmer","entrepreneur","salaried","self-employed","unemployed","homemaker","retired"];

const DEFAULT_FORM = {
  name: "",
  age: "",
  gender: "male",
  income: "",
  occupation: "farmer",
  state: "Maharashtra",
  is_bpl: false,
  has_aadhaar: true,
  has_bank_account: true,
  has_land_records: false,
  has_pan: false,
};

function Badge({ label, color }) {
  const colors = {
    green: { bg: "#d1fae5", text: "#065f46", border: "#6ee7b7" },
    yellow: { bg: "#fef9c3", text: "#854d0e", border: "#fde047" },
    red: { bg: "#fee2e2", text: "#991b1b", border: "#fca5a5" },
    blue: { bg: "#dbeafe", text: "#1e40af", border: "#93c5fd" },
  };
  const c = colors[color] || colors.blue;
  return (
    <span style={{
      background: c.bg, color: c.text, border: `1px solid ${c.border}`,
      borderRadius: 20, padding: "2px 12px", fontSize: 12, fontWeight: 600,
    }}>
      {label}
    </span>
  );
}

function SchemeCard({ result, rank }) {
  const [open, setOpen] = useState(false);
  const eligColor = result.is_eligible ? "green" : result.readiness_score >= 50 ? "yellow" : "red";
  const eligLabel = result.is_eligible ? "✓ Eligible" : result.readiness_score >= 50 ? "~ Partial" : "✗ Ineligible";

  return (
    <div className="scheme-card" style={{ borderLeft: `4px solid ${eligColor === "green" ? "#10b981" : eligColor === "yellow" ? "#f59e0b" : "#ef4444"}` }}>
      <div className="scheme-header" onClick={() => setOpen(!open)} style={{ cursor: "pointer" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span className="rank-badge">#{rank}</span>
          <div>
            <div className="scheme-name">{result.scheme_name}</div>
            <div className="scheme-ministry">{result.ministry}</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div className="score-ring">
            <span>{result.readiness_score}%</span>
          </div>
          <Badge label={eligLabel} color={eligColor} />
          <span style={{ fontSize: 18, color: "#6b7280" }}>{open ? "▲" : "▼"}</span>
        </div>
      </div>

      {open && (
        <div className="scheme-body">
          {result.scheme_description && (
            <p className="scheme-desc">{result.scheme_description}</p>
          )}
          <div className="scheme-grid">
            {result.benefit_amount && (
              <div className="info-chip">
                <span className="chip-label">💰 Benefit</span>
                <span>{result.benefit_amount}</span>
              </div>
            )}
            {result.application_mode && (
              <div className="info-chip">
                <span className="chip-label">📋 Apply via</span>
                <span>{result.application_mode}</span>
              </div>
            )}
            {result.deadline && (
              <div className="info-chip">
                <span className="chip-label">📅 Deadline</span>
                <span>{result.deadline}</span>
              </div>
            )}
          </div>
          {result.matched_criteria?.length > 0 && (
            <div className="criteria-section">
              <div className="criteria-title">✅ Matched criteria</div>
              <ul>{result.matched_criteria.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </div>
          )}
          {result.missing_documents?.length > 0 && (
            <div className="criteria-section missing">
              <div className="criteria-title">📎 Missing documents</div>
              <ul>{result.missing_documents.map((d, i) => <li key={i}>{d}</li>)}</ul>
            </div>
          )}
          {result.next_steps?.length > 0 && (
            <div className="criteria-section next">
              <div className="criteria-title">👉 Next steps</div>
              <ol>{result.next_steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
            </div>
          )}
          {result.portal_link && (
            <a href={result.portal_link} target="_blank" rel="noreferrer" className="apply-btn">
              Apply Now →
            </a>
          )}
        </div>
      )}
    </div>
  );
}

function App() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");
  const [tab, setTab] = useState("form");

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }));

  const handleSubmit = async () => {
    if (!form.name.trim()) { setError("Please enter your name."); return; }
    if (!form.age || isNaN(form.age) || form.age < 1 || form.age > 120) { setError("Please enter a valid age."); return; }
    if (!form.income || isNaN(form.income)) { setError("Please enter a valid annual income."); return; }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const payload = { ...form, age: parseInt(form.age), income: parseFloat(form.income) };
      const res = await fetch("http://localhost:8000/api/v1/match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const result = await res.json();
      setData(result);
      setTab("results");
    } catch (e) {
      setError(e.message.includes("Failed to fetch")
        ? "Could not connect to the backend. Make sure the server is running on http://localhost:8000."
        : e.message);
    } finally {
      setLoading(false);
    }
  };

  const filtered = data?.results?.filter(r => {
    if (filter === "eligible") return r.is_eligible;
    if (filter === "partial") return !r.is_eligible && r.readiness_score >= 50;
    if (filter === "ineligible") return !r.is_eligible && r.readiness_score < 50;
    return true;
  }) ?? [];

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">🏛️</span>
            <div>
              <div className="logo-title">SaralSewa</div>
              <div className="logo-sub">Government Scheme Matcher</div>
            </div>
          </div>
          {data && (
            <div className="header-stats">
              <div className="stat"><span className="stat-num green">{data.eligible_count ?? 0}</span><span>Eligible</span></div>
              <div className="stat"><span className="stat-num yellow">{data.partially_eligible_count ?? 0}</span><span>Partial</span></div>
              <div className="stat"><span className="stat-num">{data.total_schemes_checked ?? 0}</span><span>Checked</span></div>
            </div>
          )}
        </div>
        {data && (
          <div className="tabs">
            <button className={`tab ${tab === "form" ? "active" : ""}`} onClick={() => setTab("form")}>📝 Edit Profile</button>
            <button className={`tab ${tab === "results" ? "active" : ""}`} onClick={() => setTab("results")}>📊 Results ({data.results?.length ?? 0})</button>
          </div>
        )}
      </header>

      <main className="main">
        {tab === "form" && (
          <div className="form-container">
            <div className="form-card">
              <h2>Your Profile</h2>
              <p className="form-intro">Fill in your details to find government schemes you qualify for.</p>
              <div className="form-grid">
                <div className="field">
                  <label>Full Name *</label>
                  <input value={form.name} onChange={e => set("name", e.target.value)} placeholder="e.g. Ramesh Kumar" />
                </div>
                <div className="field">
                  <label>Age *</label>
                  <input type="number" value={form.age} onChange={e => set("age", e.target.value)} placeholder="e.g. 35" min="1" max="120" />
                </div>
                <div className="field">
                  <label>Gender</label>
                  <select value={form.gender} onChange={e => set("gender", e.target.value)}>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div className="field">
                  <label>Annual Income (₹) *</label>
                  <input type="number" value={form.income} onChange={e => set("income", e.target.value)} placeholder="e.g. 150000" />
                </div>
                <div className="field">
                  <label>Occupation</label>
                  <select value={form.occupation} onChange={e => set("occupation", e.target.value)}>
                    {OCCUPATIONS.map(o => <option key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>)}
                  </select>
                </div>
                <div className="field">
                  <label>State</label>
                  <select value={form.state} onChange={e => set("state", e.target.value)}>
                    {STATES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>
              <div className="checkbox-section">
                <h3>Documents & Status</h3>
                <div className="checkbox-grid">
                  {[
                    ["is_bpl", "Below Poverty Line (BPL)"],
                    ["has_aadhaar", "Has Aadhaar Card"],
                    ["has_bank_account", "Has Bank Account"],
                    ["has_land_records", "Has Land Records"],
                    ["has_pan", "Has PAN Card"],
                  ].map(([key, label]) => (
                    <label key={key} className="checkbox-label">
                      <input type="checkbox" checked={form[key]} onChange={e => set(key, e.target.checked)} />
                      <span>{label}</span>
                    </label>
                  ))}
                </div>
              </div>
              {error && <div className="error-box">⚠️ {error}</div>}
              <button className="submit-btn" onClick={handleSubmit} disabled={loading}>
                {loading ? <><span className="spinner" /> Checking schemes…</> : "🔍 Find My Schemes"}
              </button>
            </div>
          </div>
        )}

        {tab === "results" && data && (
          <div className="results-container">
            <div className="results-header">
              <div>
                <h2>Results for <strong>{data.user_name}</strong></h2>
                {data.top_recommendation && (
                  <div className="top-rec">⭐ Top recommendation: <strong>{data.top_recommendation}</strong></div>
                )}
              </div>
              <div className="filter-bar">
                {["all", "eligible", "partial", "ineligible"].map(f => (
                  <button key={f} className={`filter-btn ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>
                    {f.charAt(0).toUpperCase() + f.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            {filtered.length === 0
              ? <div className="empty">No schemes match this filter.</div>
              : filtered.map((r, i) => <SchemeCard key={i} result={r} rank={r.relevance_rank ?? i + 1} />)
            }
          </div>
        )}
      </main>

      <footer className="app-footer">
        SaralSewa • InnovaHack 2026 • Data sourced from official government portals
      </footer>
    </div>
  );
}

export default App;
