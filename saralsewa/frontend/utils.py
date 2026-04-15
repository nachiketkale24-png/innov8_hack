# frontend/utils.py

def generate_suggestions(results):
    """Generates detailed action points based on document gaps."""
    suggestions = []
    for r in results:
        # Check if the keys exist before accessing to prevent crashes
        if r.get("is_eligible") and r.get("missing_documents"):
            docs = ", ".join(r["missing_documents"])
            suggestions.append(
                f"**{r['scheme_name']}**: Priority! Please apply for/renew: {docs}."
            )
    return suggestions

def get_localized_strings(lang="EN"):
    """Dictionary for multi-language support (English/Hindi)."""
    dictionary = {
        "EN": {
            "title": "SaralSewa – AI Governance Copilot",
            "sidebar_header": "Citizen Profile",
            "check_btn": "Check My Eligibility",
            "loading": "Analyzing 100+ policy parameters...",
            "hero_sub": "Empowering citizens with AI-driven policy matching.",
        },
        "HI": {
            "title": "सरलसेवा – एआई गवर्नेंस कोपायलट",
            "sidebar_header": "नागरिक प्रोफ़ाइल",
            "check_btn": "मेरी पात्रता जांचें",
            "loading": "नीति मापदंडों का विश्लेषण कर रहा है...",
            "hero_sub": "एआई-संचालित नीति मिलान के साथ नागरिकों को सशक्त बनाना।",
        }
    }
    return dictionary.get(lang, dictionary["EN"])