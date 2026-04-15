# frontend/utils.py

def calculate_readiness_score(results):
    """
    Calculates an overall readiness percentage across all schemes.
    Useful for the dashboard metrics.
    """
    if not results:
        return 0
    total_score = sum([r.get("readiness_score", 0) for r in results])
    return round(total_score / len(results), 2)

def get_nearest_centers(state):
    """
    Returns simulated local government office addresses based on state.
    This adds a 'Local Impact' feel to the app.
    """
    centers = {
        "Maharashtra": ["Aaple Sarkar Seva Kendra, Mumbai", "Collector Office, Pune"],
        "Uttar Pradesh": ["Jan Seva Kendra, Lucknow", "Vikas Bhawan, Kanpur"],
        "Delhi": ["SDM Office, Chanakyapuri", "Doorstep Delivery Service (1076)"],
        "Karnataka": ["Bangalore One Center", "Nadakacheri, Mysuru"]
    }
    return centers.get(state, ["Local Tehsildar Office", "Common Service Center (CSC)"])

def generate_suggestions(results):
    """
    Enhanced: Generates actionable advice with priority levels.
    """
    suggestions = []
    for r in results:
        # Check eligibility and if documents are missing
        is_eligible = r.get("is_eligible", False)
        missing_docs = r.get("missing_documents", [])
        
        if is_eligible and not missing_docs:
            suggestions.append(f"✅ **{r['scheme_name']}**: You are 100% ready! Proceed to apply immediately.")
        
        elif is_eligible and missing_docs:
            docs_text = ", ".join(missing_docs)
            suggestions.append(f"⚠️ **{r['scheme_name']}**: Eligible, but need documents: **{docs_text}**.")
            
        elif not is_eligible and r.get("readiness_score", 0) > 70:
            suggestions.append(f"ℹ️ **{r['scheme_name']}**: Close match! Review income or age criteria.")
            
    return suggestions if suggestions else ["No immediate actions required. Your profile is up to date."]

def get_localized_strings(lang="EN"):
    """
    Expanded dictionary for multi-language support (English/Hindi).
    Added more UI keys for a complete translation.
    """
    dictionary = {
        "EN": {
            "title": "SaralSewa – AI Governance Copilot",
            "sidebar_header": "Citizen Profile",
            "check_btn": "Check My Eligibility",
            "loading": "Analyzing 100+ policy parameters...",
            "hero_sub": "Empowering citizens with AI-driven policy matching.",
            "readiness": "Profile Readiness Score",
            "nearest_center": "Visit Nearest Center",
            "export_btn": "Download Report",
            "lang_label": "Select Language / भाषा चुनें"
        },
        "HI": {
            "title": "सरलसेवा – एआई गवर्नेंस कोपायलट",
            "sidebar_header": "नागरिक प्रोफ़ाइल",
            "check_btn": "मेरी पात्रता जांचें",
            "loading": "नीति मापदंडों का विश्लेषण कर रहा है...",
            "hero_sub": "एआई-संचालित नीति मिलान के साथ नागरिकों को सशक्त बनाना।",
            "readiness": "प्रोफ़ाइल तैयारी स्कोर",
            "nearest_center": "नज़दीकी केंद्र पर जाएँ",
            "export_btn": "रिपोर्ट डाउनलोड करें",
            "lang_label": "भाषा चुनें"
        }
    }
    return dictionary.get(lang, dictionary["EN"])