"""
CivicMatch Core Orchestrator
"""

from typing import List

from services.data_loader import load_schemes
from services.eligibility_engine import check_eligibility
from services.scoring import check_documents, compute_readiness_score
from services.explanation_engine import (
    generate_missing_conditions,
    build_action_steps,
)
from models.schemas import EligibilityResult, MatchResponse, UserProfile

from services.supabase_client import supabase


def run_civic_match(user_profile: UserProfile) -> MatchResponse:
    user = user_profile.model_dump()
    schemes = load_schemes()

    # Category filter
    if user_profile.category_filter:
        schemes = [
            s for s in schemes
            if s["category"].lower() == user_profile.category_filter.lower()
        ]

    results: List[EligibilityResult] = []
    eligible_count = 0
    partial_count = 0
    ineligible_count = 0

    for scheme in schemes:

        is_eligible, pass_reasons, fail_reasons = check_eligibility(user, scheme)

        available_docs, missing_docs = check_documents(user, scheme)

        missing_conditions = generate_missing_conditions(
            user, scheme, fail_reasons, missing_docs
        )

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

        action_steps = build_action_steps(
            scheme=scheme,
            is_eligible=is_eligible,
            missing_docs=missing_docs,
            missing_conditions=missing_conditions,
        )

        summary = summarize_eligibility(
            scheme_name=scheme["name"],
            is_eligible=is_eligible,
            readiness_score=score,
            pass_reasons=pass_reasons,
            fail_reasons=fail_reasons,
            missing_docs=missing_docs,
        )

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
                ministry=scheme.get("ministry", ""),
                is_eligible=is_eligible,
                readiness_score=score,
                eligibility_reasons=pass_reasons,
                ineligibility_reasons=fail_reasons,
                missing_documents=missing_docs,
                missing_conditions=missing_conditions,
                action_steps=action_steps,
            )
        )

    # Ranking
    scheme_weight_map = {s["id"]: s.get("weight", 5) for s in schemes}

    def rank_key(r: EligibilityResult):
        eligible_bonus = 1000 if r.is_eligible else 0
        return eligible_bonus + r.readiness_score * scheme_weight_map.get(r.scheme_id, 5)

    results.sort(key=rank_key, reverse=True)

    for i, r in enumerate(results):
        r.relevance_rank = i + 1

    top = results[0].scheme_name if results else None
    top_id = results[0].scheme_id if results else None

    avg_score = (
        round(sum(r.readiness_score for r in results) / len(results), 1)
        if results else 0.0
    )

       # 🔥 SUPABASE SAVE
    print("🔥 Trying to save to Supabase...")

    try:
        supabase.table("match_results").insert({
            "user_name": user_profile.name,
            "total_schemes": len(schemes),
            "eligible": eligible_count,
            "partial": partial_count,
            "ineligible": ineligible_count,
            "top_scheme": top
        }).execute()

        print("✅ Saved to Supabase")

    except Exception as e:
        print("❌ Supabase error:", e)

    return MatchResponse(
        user_name=user_profile.name,
        total_schemes_checked=len(schemes),
        eligible_count=eligible_count,
        partially_eligible_count=partial_count,
        ineligible_count=ineligible_count,
        results=results,
        top_recommendation=top,
        top_recommendation_id=top_id,
        average_readiness_score=avg_score,
    )