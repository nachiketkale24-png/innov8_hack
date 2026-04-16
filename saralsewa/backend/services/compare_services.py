"""
Scheme Comparison Service
--------------------------
Given a list of scheme IDs + user profile,
returns a side-by-side comparison with a ranked recommendation.
"""

from typing import List, Dict, Any

from backend.services.data_loader import load_schemes
from backend.services.eligibility_engine import check_eligibility
from backend.services.scoring import check_documents, compute_readiness_score
from backend.models.schemas import SchemeCompareItem, CompareResponse, UserProfile


_BEST_FOR_MAP = {
    "Agriculture":        "Small/marginal farmers with land records",
    "Financial Inclusion": "Anyone without a formal bank account",
    "Housing":            "Rural BPL families needing a pucca house",
    "Insurance":          "Workers needing low-cost accident protection",
    "Entrepreneurship":   "Self-employed & micro-business owners",
}


def compare_schemes(scheme_ids: List[str], user: UserProfile) -> CompareResponse:
    all_schemes = load_schemes()
    scheme_map = {s["id"]: s for s in all_schemes}
    user_dict = user.model_dump()

    items: List[SchemeCompareItem] = []
    for sid in scheme_ids:
        scheme = scheme_map.get(sid)
        if not scheme:
            continue

        is_eligible, pass_reasons, fail_reasons = check_eligibility(user_dict, scheme)
        available_docs, missing_docs = check_documents(user_dict, scheme)
        total_rules = len(pass_reasons) + len(fail_reasons)
        total_docs = len(scheme.get("required_documents", []))

        score = compute_readiness_score(
            is_eligible=is_eligible,
            fail_count=len(fail_reasons),
            total_rules=total_rules,
            available_docs=available_docs,
            total_docs=total_docs,
            missing_conditions=[],
        )

        key_reqs = scheme.get("required_documents", [])[:3]

        items.append(SchemeCompareItem(
            scheme_id=sid,
            scheme_name=scheme["name"],
            benefit=scheme["benefit"],
            readiness_score=score,
            is_eligible=is_eligible,
            key_requirements=key_reqs,
            missing_docs=missing_docs,
            best_for=_BEST_FOR_MAP.get(scheme["category"], scheme["category"]),
        ))

    # Sort by score desc
    items.sort(key=lambda x: (x.is_eligible, x.readiness_score), reverse=True)

    if items:
        top = items[0]
        reasoning = (
            f"'{top.scheme_name}' is the best match for {user.name} "
            f"with a readiness score of {top.readiness_score}% "
            f"({'fully eligible' if top.is_eligible else 'partially eligible'})."
        )
        if top.missing_docs:
            reasoning += f" Only {len(top.missing_docs)} document(s) still needed."
        recommendation = top.scheme_name
    else:
        recommendation = "None"
        reasoning = "No matching schemes found for the given IDs."

    return CompareResponse(items=items, recommendation=recommendation, reasoning=reasoning)