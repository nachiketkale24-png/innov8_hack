from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any


class UserProfile(BaseModel):
    name: str = Field(..., description="Full name of the applicant", min_length=2)
    age: int = Field(..., ge=1, le=120, description="Age in years")
    gender: str = Field(..., description="male / female / other")
    income: int = Field(..., ge=0, description="Annual household income in INR")
    occupation: str = Field(..., description="e.g. farmer, self_employed, salaried, unemployed")
    state: str = Field(..., description="Indian state name")
    is_bpl: bool = Field(default=False, description="Whether the user holds a BPL card")
    has_aadhaar: bool = Field(default=True, description="Whether Aadhaar card is available")
    has_bank_account: bool = Field(default=True, description="Whether user has a bank account")
    has_land_records: bool = Field(default=False, description="Whether user has land records")
    has_pan: bool = Field(default=False, description="Whether user has PAN card")
    # FIX: Added category_filter field so frontend can filter by category
    category_filter: Optional[str] = Field(default=None, description="Filter results by scheme category")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v):
        allowed = {"male", "female", "other", "prefer_not_to_say"}
        if v.lower() not in allowed:
            raise ValueError(f"gender must be one of: {', '.join(allowed)}")
        return v.lower()

    @field_validator("occupation")
    @classmethod
    def validate_occupation(cls, v):
        return v.strip().lower()

    @field_validator("state")
    @classmethod
    def validate_state(cls, v):
        return v.strip()


class EligibilityResult(BaseModel):
    scheme_id: str
    scheme_name: str
    category: str
    benefit: str
    ministry: str = ""          # FIX: was missing ministry in results
    is_eligible: bool
    readiness_score: float = Field(..., ge=0.0, le=100.0, description="0-100 readiness %")
    eligibility_reasons: List[str]
    ineligibility_reasons: List[str]
    missing_documents: List[str]
    missing_conditions: List[str]
    action_steps: List[str]
    tags: List[str] = []        # FIX: added tags to result for frontend display
    relevance_rank: Optional[int] = None


class MatchResponse(BaseModel):
    user_name: str
    total_schemes_checked: int
    eligible_count: int
    partially_eligible_count: int
    ineligible_count: int
    results: List[EligibilityResult]
    top_recommendation: Optional[str] = None