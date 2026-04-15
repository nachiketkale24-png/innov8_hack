"""
Quick smoke-test for CivicMatch logic (no server needed).
Run from the saralsewa/ directory:
    python test_civic_match.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from backend.models.schemas import UserProfile
from backend.services.civic_match import run_civic_match

def test_farmer():
    user = UserProfile(
        name="Ramesh Kumar",
        age=38,
        gender="male",
        income=90000,
        occupation="farmer",
        state="Rajasthan",
        is_bpl=True,
        has_aadhaar=True,
        has_bank_account=True,
        has_land_records=True,
        has_pan=False,
    )
    result = run_civic_match(user)
    print(f"\n{'='*60}")
    print(f"User: {result.user_name}")
    print(f"Schemes checked: {result.total_schemes_checked}")
    print(f"Eligible: {result.eligible_count} | Partial: {result.partially_eligible_count} | Ineligible: {result.ineligible_count}")
    print(f"Top Recommendation: {result.top_recommendation}")
    print(f"\n--- Top 3 Results ---")
    for r in result.results[:3]:
        print(f"\n#{r.relevance_rank} {r.scheme_name}")
        print(f"   Eligible: {r.is_eligible} | Score: {r.readiness_score}%")
        if r.missing_documents:
            print(f"   Missing docs: {r.missing_documents}")
    print(f"{'='*60}\n")

def test_entrepreneur():
    user = UserProfile(
        name="Priya Singh",
        age=27,
        gender="female",
        income=300000,
        occupation="entrepreneur",
        state="Maharashtra",
        is_bpl=False,
        has_aadhaar=True,
        has_bank_account=True,
        has_land_records=False,
        has_pan=True,
    )
    result = run_civic_match(user)
    print(f"\n{'='*60}")
    print(f"User: {result.user_name}")
    print(f"Eligible: {result.eligible_count} | Partial: {result.partially_eligible_count} | Ineligible: {result.ineligible_count}")
    print(f"Top Recommendation: {result.top_recommendation}")
    for r in result.results[:3]:
        print(f"  #{r.relevance_rank} {r.scheme_name} → Score: {r.readiness_score}%")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("Running CivicMatch smoke tests...")
    test_farmer()
    test_entrepreneur()
    print("All tests passed ✅")