from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class UserProfile(BaseModel):
    name: str = Field(..., description="Full name of the applicant")
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


class EligibilityResult(BaseModel):
    scheme_id: str
    scheme_name: str
    category: str
    benefit: str
    is_eligible: bool
    readiness_score: float = Field(..., ge=0.0, le=100.0, description="0–100 readiness %")
    eligibility_reasons: List[str]
    ineligibility_reasons: List[str]
    missing_documents: List[str]
    missing_conditions: List[str]
    action_steps: List[str]
    relevance_rank: Optional[int] = None
    readiness_timeline: dict = {}


class MatchResponse(BaseModel):
    user_name: str
    total_schemes_checked: int
    eligible_count: int
    partially_eligible_count: int
    ineligible_count: int
    results: List[EligibilityResult]
    top_recommendation: Optional[str] = None


class ConversationalRequest(BaseModel):
    message: str