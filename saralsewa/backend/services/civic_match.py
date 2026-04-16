"""
CivicMatch Core Orchestrator
------------------------------
Ties together:
  data_loader → eligibility_engine → scoring → explanation_engine

Returns a fully structured MatchResponse.
"""

from typing import Dict, Any, List

from backend.services.data_loader import load_schemes
from backend.services.eligibility_engine import check_eligibility
from backend.services.scoring import check_documents, compute_readiness_score
from backend.services.explanation_engine import (
    generate_missing_conditions,
    build_action_steps,
    calculate_readiness_timeline,
)
from backend.models.schemas import EligibilityResult, MatchResponse, UserProfile


def run_civic_match(user_profile: UserProfile) -> MatchResponse:
    user = user_profile.model_dump()
    schemes = load_schemes()

    results: List[EligibilityResult] = []
    eligible_count = 0
    partial_count = 0
    ineligible_count = 0

    for scheme in schemes:
        # 1. Eligibility check
        is_eligible, pass_reasons, fail_reasons = check_eligibility(user, scheme)

        # 2. Document check
        available_docs, missing_docs = check_documents(user, scheme)

        # 3. Missing conditions (actionable gaps)
        missing_conditions = generate_missing_conditions(
            user, scheme, fail_reasons, missing_docs
        )

        # 4. Readiness score
        total_rules = len(pass_reasons) + len(fail_reasons)
        total_docs = len(scheme.get("required_documents", []))

        score = compute_readiness_score(
            is_eligible=is_eligible,
            fail_count=len(fail_reasons),
            total_rules=total_rules,
            available_docs=available_docs,
            total_docs=total_docs,
            missing_conditions=missing_conditions,
        )

        # 5. Action steps
        action_steps = build_action_steps(
            scheme=scheme,
            is_eligible=is_eligible,
            missing_docs=missing_docs,
            missing_conditions=missing_conditions,
        )

        # 6. Counters
        if is_eligible and score >= 80:
            eligible_count += 1
        elif is_eligible:
            partial_count += 1
        else:
            ineligible_count += 1

        results.append(
            EligibilityResult(
                scheme_id=scheme["id"],
                scheme_name=scheme["name"],
                category=scheme["category"],
                benefit=scheme["benefit"],
                is_eligible=is_eligible,
                readiness_score=score,
                eligibility_reasons=pass_reasons,
                ineligibility_reasons=fail_reasons,
                missing_documents=missing_docs,
                missing_conditions=missing_conditions,
                action_steps=action_steps,
                readiness_timeline=calculate_readiness_timeline(missing_docs),
            )
        )

    # Rank by (eligibility + score * weight)
    scheme_weight_map = {s["id"]: s.get("weight", 5) for s in schemes}

    def rank_key(r: EligibilityResult):
        eligible_bonus = 1000 if r.is_eligible else 0
        return eligible_bonus + r.readiness_score * scheme_weight_map.get(r.scheme_id, 5)

    results.sort(key=rank_key, reverse=True)
    for i, r in enumerate(results):
        r.relevance_rank = i + 1

    top = results[0].scheme_name if results else None

    return MatchResponse(
        user_name=user_profile.name,
        total_schemes_checked=len(schemes),
        eligible_count=eligible_count,
        partially_eligible_count=partial_count,
        ineligible_count=ineligible_count,
        results=results,
        top_recommendation=top,
    )