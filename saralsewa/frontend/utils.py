# frontend/utils.py

def generate_suggestions(results):
    """
    Generates detailed, prioritized action points based on eligibility gaps.
    FIX: Was only checking eligible schemes with missing docs.
         Now also surfaces near-miss ineligible schemes with high readiness scores.
    """
    suggestions = []

    # Priority 1: Eligible but docs missing
    for r in results:
        if r.get("is_eligible") and r.get("missing_documents"):
            docs = ", ".join(r["missing_documents"])
            suggestions.append(
                f"**Priority Action – {r['scheme_name']}**: You qualify! "
                f"Just gather these documents to apply: {docs}."
            )

    # FIX: Priority 2: Near-miss schemes (score >= 60 but not eligible)
    for r in results:
        if not r.get("is_eligible") and r.get("readiness_score", 0) >= 60:
            conditions = r.get("missing_conditions", [])
            if conditions:
                tip = conditions[0]
                suggestions.append(
                    f"**Close Call – {r['scheme_name']}**: "
                    f"You are {r['readiness_score']}% ready. Key action: {tip}"
                )

    # FIX: Priority 3: Insurance schemes that are easy to enroll in
    for r in results:
        if r.get("is_eligible") and r.get("category") == "Insurance" and not r.get("missing_documents"):
            suggestions.append(
                f"**Quick Win – {r['scheme_name']}**: "
                f"You are fully eligible for this low-cost insurance. Enroll today!"
            )

    return suggestions[:5]  # Top 5 suggestions


def get_localized_strings(lang="EN"):
    """
    Dictionary for multi-language support (English/Hindi/Marathi).
    FIX: Added Marathi support; fixed missing 'hero_sub' style class.
    """
    dictionary = {
        "EN": {
            "title": "SaralSewa – AI Governance Copilot",
            "sidebar_header": "Citizen Profile",
            "check_btn": "Check My Eligibility",
            "loading": "Analyzing 200+ policy parameters...",
            "hero_sub": "Empowering citizens with AI-driven policy matching for 15+ government schemes.",
            "eligible_label": "Eligible",
            "not_eligible_label": "Not Eligible",
            "partial_label": "Partially Ready",
            "readiness_label": "Readiness Score",
            "top_rec_label": "AI Priority Recommendation",
            "suggestions_label": "Smart Suggestions",
            "export_label": "Export Your Results",
        },
        "HI": {
            "title": "सरलसेवा – एआई गवर्नेंस कोपायलट",
            "sidebar_header": "नागरिक प्रोफ़ाइल",
            "check_btn": "मेरी पात्रता जांचें",
            "loading": "नीति मापदंडों का विश्लेषण हो रहा है...",
            "hero_sub": "एआई-संचालित नीति मिलान के साथ 15+ सरकारी योजनाओं में नागरिकों को सशक्त बनाना।",
            "eligible_label": "पात्र",
            "not_eligible_label": "अपात्र",
            "partial_label": "आंशिक रूप से तैयार",
            "readiness_label": "तत्परता स्कोर",
            "top_rec_label": "AI प्राथमिकता सिफारिश",
            "suggestions_label": "स्मार्ट सुझाव",
            "export_label": "परिणाम निर्यात करें",
        },
        "MR": {
            "title": "सरळसेवा – AI शासन सहाय्यक",
            "sidebar_header": "नागरिक प्रोफाइल",
            "check_btn": "माझी पात्रता तपासा",
            "loading": "धोरण मापदंडांचे विश्लेषण सुरू आहे...",
            "hero_sub": "AI-चालित धोरण जुळणीद्वारे 15+ सरकारी योजनांमध्ये नागरिकांना सक्षम करणे.",
            "eligible_label": "पात्र",
            "not_eligible_label": "अपात्र",
            "partial_label": "अंशतः तयार",
            "readiness_label": "तयारी गुण",
            "top_rec_label": "AI प्राधान्य शिफारस",
            "suggestions_label": "स्मार्ट सूचना",
            "export_label": "निकाल निर्यात करा",
        },
    }
    return dictionary.get(lang, dictionary["EN"])


def format_income(amount: int) -> str:
    """Format income as Indian number system (lakhs/crores)."""
    if amount >= 10_000_000:
        return f"Rs.{amount / 10_000_000:.1f} Cr"
    elif amount >= 100_000:
        return f"Rs.{amount / 100_000:.1f} L"
    else:
        return f"Rs.{amount:,}"


def get_score_color(score: float) -> str:
    """Return color hex for a readiness score."""
    if score >= 80:
        return "#16a34a"   # green
    elif score >= 60:
        return "#ca8a04"   # yellow
    elif score >= 40:
        return "#ea580c"   # orange
    else:
        return "#dc2626"   # red


def get_category_icon(category: str) -> str:
    """Return emoji icon for a scheme category."""
    icons = {
        "Agriculture": "🌾",
        "Financial Inclusion": "🏦",
        "Housing": "🏠",
        "Insurance": "🛡️",
        "Entrepreneurship": "💼",
        "Pension": "👴",
        "Education": "📚",
        "Skill Development": "🔧",
        "Women & Child": "👩‍👧",
        "Food Security": "🍚",
        "Energy & Welfare": "⚡",
        "Urban Livelihood": "🏙️",
        "Employment": "👷",
    }
    return icons.get(category, "📋")