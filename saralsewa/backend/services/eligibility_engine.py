"""
Eligibility Engine
------------------
Rule-based eligibility checker.  For each scheme it checks:
  1. Age range
  2. Income ceiling
  3. Occupation match
  4. Gender match
  5. State applicability
  6. Exclusion categories
  7. Special flags (BPL, etc.)

Returns structured pass / fail reasons per rule.
"""

from typing import Dict, Any, List, Tuple

# Map free-text occupations the user might type to canonical tags
OCCUPATION_ALIASES: Dict[str, List[str]] = {
    "farmer":        ["farmer", "agriculture", "agriculturist", "kisan"],
    "self_employed": ["self_employed", "business", "freelance", "vendor", "trader"],
    "small_business":["small_business", "shopkeeper", "msme", "entrepreneur"],
    "entrepreneur":  ["entrepreneur", "startup", "founder"],
    "salaried":      ["salaried", "employee", "private_sector", "corporate"],
    "government_employee": ["government_employee", "govt_employee", "psu", "civil_servant"],
    "unemployed":    ["unemployed", "job_seeker", "student"],
    "retired":       ["retired", "pensioner"],
    "homemaker":     ["homemaker", "housewife"],
}


def _normalize_occupation(raw: str) -> str:
    """Return the canonical occupation key for a raw input string."""
    raw_lower = raw.strip().lower().replace(" ", "_")
    for canonical, aliases in OCCUPATION_ALIASES.items():
        if raw_lower in aliases or raw_lower == canonical:
            return canonical
    return raw_lower


def _occupation_matches(user_occ: str, scheme_occs: Any) -> bool:
    """True when scheme_occs is 'all' or user occupation is in the list."""
    if scheme_occs == "all":
        return True
    canon = _normalize_occupation(user_occ)
    return canon in scheme_occs


def check_eligibility(
    user: Dict[str, Any],
    scheme: Dict[str, Any],
) -> Tuple[bool, List[str], List[str]]:
    """
    Returns:
        (is_eligible, pass_reasons, fail_reasons)
    """
    rules = scheme.get("eligibility_rules", {})
    pass_reasons: List[str] = []
    fail_reasons: List[str] = []

    # ── Age ──────────────────────────────────────────────────────────────────
    min_age = rules.get("min_age", 0)
    max_age = rules.get("max_age", 999)
    if min_age <= user["age"] <= max_age:
        pass_reasons.append(f"Age {user['age']} is within the required range ({min_age}–{max_age} years)")
    else:
        fail_reasons.append(
            f"Age {user['age']} is outside the required range ({min_age}–{max_age} years)"
        )

    # ── Income ───────────────────────────────────────────────────────────────
    max_income = rules.get("max_income", float("inf"))
    if user["income"] <= max_income:
        pass_reasons.append(
            f"Annual income ₹{user['income']:,} is within the limit (≤ ₹{max_income:,})"
        )
    else:
        fail_reasons.append(
            f"Annual income ₹{user['income']:,} exceeds the scheme limit of ₹{max_income:,}"
        )

    # ── Occupation ───────────────────────────────────────────────────────────
    scheme_occs = rules.get("occupation", "all")
    if _occupation_matches(user["occupation"], scheme_occs):
        pass_reasons.append(
            f"Occupation '{user['occupation']}' qualifies for this scheme"
        )
    else:
        allowed = ", ".join(scheme_occs) if isinstance(scheme_occs, list) else "all"
        fail_reasons.append(
            f"Occupation '{user['occupation']}' is not eligible (required: {allowed})"
        )

    # ── Gender ───────────────────────────────────────────────────────────────
    scheme_genders = rules.get("genders", ["male", "female", "other"])
    if user["gender"].lower() in scheme_genders:
        pass_reasons.append("Gender criteria satisfied")
    else:
        fail_reasons.append(
            f"Gender '{user['gender']}' does not meet scheme requirement ({', '.join(scheme_genders)})"
        )

    # ── State ────────────────────────────────────────────────────────────────
    scheme_states = rules.get("states", "all")
    if scheme_states == "all":
        pass_reasons.append("Scheme is available in all states including yours")
    elif user["state"].lower() in [s.lower() for s in scheme_states]:
        pass_reasons.append(f"Scheme is available in {user['state']}")
    else:
        fail_reasons.append(f"Scheme is not available in {user['state']}")

    # ── Exclusion categories ─────────────────────────────────────────────────
    excluded = rules.get("excluded_categories", [])
    canon_occ = _normalize_occupation(user["occupation"])
    if "government_employee" in excluded and canon_occ == "government_employee":
        fail_reasons.append("Government employees are excluded from this scheme")
    if "income_tax_payer" in excluded and user["income"] > 250000:
        fail_reasons.append(
            "Income tax payers (income > ₹2.5 lakh) are excluded from this scheme"
        )
    if "urban_resident" in excluded:
        # Simplified: we flag it as a warning, not a hard fail, since we don't
        # collect urban/rural from user in MVP.
        pass_reasons.append("Note: This scheme is for rural residents — verify your area type")

    # ── Special BPL requirement ───────────────────────────────────────────────
    if rules.get("requires_bpl", False):
        if user.get("is_bpl", False):
            pass_reasons.append("BPL card holder — meets BPL requirement")
        else:
            fail_reasons.append("BPL card required — user has not indicated BPL status")

    is_eligible = len(fail_reasons) == 0
    return is_eligible, pass_reasons, fail_reasons