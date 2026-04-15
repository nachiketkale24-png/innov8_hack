from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title="SaralSewa – AI Governance Copilot",
    description="CivicMatch Core: Eligibility & Readiness Engine for Indian Government Schemes",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["Root"])
def root():
    return {
        "app": "SaralSewa",
        "feature": "CivicMatch Core",
        "docs": "/docs",
        "health": "/api/v1/health",
    }