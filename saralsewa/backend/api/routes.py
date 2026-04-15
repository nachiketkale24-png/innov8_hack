from fastapi import APIRouter, HTTPException
from backend.models.schemas import UserProfile, MatchResponse
from backend.services.civic_match import run_civic_match

router = APIRouter(prefix="/api/v1", tags=["CivicMatch"])


@router.post("/match", response_model=MatchResponse, summary="Run CivicMatch eligibility check")
def match_schemes(user: UserProfile) -> MatchResponse:
    """
    Submit a user profile and receive:
    - Eligibility for each government scheme
    - Readiness score
    - Missing documents / conditions
    - Ranked results with action steps
    """
    try:
        return run_civic_match(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemes", summary="List all available schemes")
def list_schemes():
    """Return metadata of all schemes in the dataset."""
    from backend.services.data_loader import load_schemes
    schemes = load_schemes()
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "benefit": s["benefit"],
            "ministry": s["ministry"],
        }
        for s in schemes
    ]


@router.get("/health", summary="Health check")
def health():
    return {"status": "ok", "service": "SaralSewa – CivicMatch API"}