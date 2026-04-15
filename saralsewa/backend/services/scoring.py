"""
Document Checker & Readiness Scorer
-------------------------------------
Determines which required documents the user already has,
which are missing, and computes a 0–100 readiness score.

Score formula
─────────────
  readiness = (eligibility_weight * doc_weight)

  eligibility_weight:
      100  → all hard rules pass
       50  → some rules pass (partially eligible)
        0  → hard fail

  doc_weight  = docs_available / total_docs_required  (0–1)

  Final score = eligibility_weight * doc_weight
"""

from typing import Dict, Any, List, Tuple


# Map document names (lowercase keywords) to user profile fields
DOC_FIELD_MAP = {
    "aadhaar": "has_aadhaar",
    "bank account": "has_bank_account",
    "land records": "has_land_records",
    "khasra": "has_land_records",
    "pan card": "has_pan",
    "pan": "has_pan",
    "bpl ration card": "is_bpl",
    "secc": "is_bpl",          # treated as BPL-equivalent flag in MVP
}


def _user_has_document(doc_name: str, user: Dict[str, Any]) -> bool:
    """Return True if the user profile indicates they have this document."""
    doc_lower = doc_name.lower()
    for keyword, field in DOC_FIELD_MAP.items():
        if keyword in doc_lower:
            return bool(user.get(field, False))
    # Documents not in our map are assumed to be obtainable — mark as 'pending'
    # but not blocking. We treat unknown docs as potentially available.
    return True


def check_documents(
    user: Dict[str, Any],
    scheme: Dict[str, Any],
) -> Tuple[List[str], List[str]]:
    """
    Returns:
        (available_docs, missing_docs)
    """
    required = scheme.get("required_documents", [])
    available: List[str] = []
    missing: List[str] = []

    for doc in required:
        if _user_has_document(doc, user):
            available.append(doc)
        else:
            missing.append(doc)

    return available, missing


def compute_readiness_score(
    is_eligible: bool,
    fail_count: int,
    total_rules: int,
    available_docs: List[str],
    total_docs: int,
    missing_conditions: List[str],
) -> float:
    """
    Compute a 0–100 readiness score.

    Components:
      - Eligibility score  (60% weight): rules passed / total rules
      - Document score     (40% weight): docs available / total docs required
    """
    if total_rules == 0:
        eligibility_ratio = 1.0
    else:
        rules_passed = total_rules - fail_count
        eligibility_ratio = rules_passed / total_rules

    if total_docs == 0:
        doc_ratio = 1.0
    else:
        doc_ratio = len(available_docs) / total_docs

    score = (eligibility_ratio * 60) + (doc_ratio * 40)

    # Small penalty for each missing condition beyond docs
    condition_penalty = len(missing_conditions) * 5
    score = max(0.0, score - condition_penalty)

    return round(min(score, 100.0), 1)