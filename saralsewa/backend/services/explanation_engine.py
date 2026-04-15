"""
Explanation Engine
------------------
Generates human-readable, plain-language explanations for
why a user is eligible or not, and what they need to do next.
"""

from typing import List, Dict, Any


def generate_missing_conditions(
    user: Dict[str, Any],
    scheme: Dict[str, Any],
    fail_reasons: List[str],
    missing_docs: List[str],
) -> List[str]:
    """
    Derive specific actionable conditions the user needs to meet
    (beyond just missing documents).
    """
    conditions: List[str] = []
    rules = scheme.get("eligibility_rules", {})

    for reason in fail_reasons:
        if "income" in reason.lower() and "exceeds" in reason.lower():
            conditions.append(
                f"Your reported income (₹{user['income']:,}) exceeds the scheme ceiling. "
                "If your actual income qualifies, ensure correct income certificate."
            )
        elif "occupation" in reason.lower():
            allowed = rules.get("occupation", [])
            if isinstance(allowed, list):
                conditions.append(
                    f"Update your occupation to one of: {', '.join(allowed)}. "
                    "If you do multiple jobs, mention the primary one."
                )
        elif "age" in reason.lower():
            min_a = rules.get("min_age", "N/A")
            max_a = rules.get("max_age", "N/A")
            conditions.append(
                f"Age requirement: {min_a}–{max_a} years. "
                "Age-based criteria cannot be changed — this scheme does not apply."
            )
        elif "bpl" in reason.lower():
            conditions.append(
                "Obtain a BPL (Below Poverty Line) Ration Card from your local "
                "Tehsil / Block Development Office."
            )
        elif "government employee" in reason.lower():
            conditions.append(
                "This scheme excludes government employees. "
                "Check if any family member (not a govt. employee) can apply."
            )
        elif "income tax" in reason.lower():
            conditions.append(
                "This scheme is restricted to non-income-tax payers. "
                "If your taxable income is below ₹2.5 lakh, clarify with bank/CSC."
            )

    for doc in missing_docs:
        conditions.append(f"Obtain missing document: {doc}")

    return conditions


def build_action_steps(
    scheme: Dict[str, Any],
    is_eligible: bool,
    missing_docs: List[str],
    missing_conditions: List[str],
) -> List[str]:
    """
    Return a combined, ordered list of steps the user should take.
    If eligible → application steps.
    If not eligible → remediation steps first, then application steps.
    """
    steps: List[str] = []

    if not is_eligible:
        steps.append("🔧 Complete these prerequisites first:")
        for i, cond in enumerate(missing_conditions, 1):
            steps.append(f"  {i}. {cond}")
        if missing_docs:
            steps.append("📄 Gather these missing documents:")
            for doc in missing_docs:
                steps.append(f"  • {doc}")
        steps.append("─────────────────────────────────────")

    app_steps = scheme.get("application_steps", [])
    if app_steps:
        steps.append("📋 Application Steps:")
        for i, step in enumerate(app_steps, 1):
            steps.append(f"  {i}. {step}")

    return steps


def summarize_eligibility(
    scheme_name: str,
    is_eligible: bool,
    readiness_score: float,
    pass_reasons: List[str],
    fail_reasons: List[str],
    missing_docs: List[str],
) -> str:
    """Single-paragraph plain-English summary (used in API description field)."""
    if is_eligible and readiness_score >= 80:
        status = (
            f"✅ You are ELIGIBLE for {scheme_name}. "
            f"Your readiness score is {readiness_score}%. "
            "You appear to meet all key criteria."
        )
    elif is_eligible and readiness_score >= 50:
        doc_note = (
            f" However, {len(missing_docs)} document(s) are missing."
            if missing_docs
            else ""
        )
        status = (
            f"🟡 You are ELIGIBLE for {scheme_name} but not fully prepared. "
            f"Readiness score: {readiness_score}%.{doc_note}"
        )
    else:
        num_fails = len(fail_reasons)
        status = (
            f"❌ You are currently NOT ELIGIBLE for {scheme_name}. "
            f"{num_fails} eligibility rule(s) not met. "
            f"Readiness score: {readiness_score}%."
        )
    return status