from fastapi import APIRouter, HTTPException, Query
from typing import Optional

# ✅ FIXED imports (removed 'backend.')
from models.schemas import UserProfile, MatchResponse
from services.civic_match import run_civic_match

router = APIRouter(tags=["CivicMatch"])  # ❗ no prefix here


@router.post("/match", response_model=MatchResponse, summary="Run CivicMatch eligibility check")
def match_schemes(user: UserProfile) -> MatchResponse:
    try:
        return run_civic_match(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemes", summary="List all available schemes")
def list_schemes(category: Optional[str] = Query(None, description="Filter by category")):
    from services.data_loader import load_schemes

    schemes = load_schemes()

    result = [
        {
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "benefit": s["benefit"],
            "ministry": s["ministry"],
            "tags": s.get("tags", []),
        }
        for s in schemes
    ]

    if category:
        result = [s for s in result if s["category"].lower() == category.lower()]

    return result


@router.get("/schemes/categories", summary="List all scheme categories")
def list_categories():
    from services.data_loader import load_schemes

    schemes = load_schemes()
    categories = sorted(set(s["category"] for s in schemes))

    return {"categories": categories, "total": len(categories)}


@router.get("/schemes/{scheme_id}", summary="Get single scheme detail")
def get_scheme(scheme_id: str):
    from services.data_loader import load_schemes

    schemes = load_schemes()

    for s in schemes:
        if s["id"].lower() == scheme_id.lower():
            return s

    raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")


@router.get("/stats", summary="Scheme database statistics")
def get_stats():
    from services.data_loader import load_schemes
    from collections import Counter

    schemes = load_schemes()
    categories = Counter(s["category"] for s in schemes)

    return {
        "total_schemes": len(schemes),
        "categories": dict(categories),
        "last_updated": "2025-01-01",
    }


@router.get("/health", summary="Health check")
def health():
    return {
        "status": "ok",
        "service": "SaralSewa – CivicMatch API",
        "version": "2.0.0",
    }