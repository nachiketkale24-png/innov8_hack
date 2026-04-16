"""
SaralSewa – AI Governance Copilot
FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="SaralSewa – AI Governance Copilot",
    description="CivicMatch Core: Eligibility & Readiness Engine for Indian Government Schemes",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router,prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {
        "app": "SaralSewa",
        "feature": "CivicMatch Core",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "schemes": "/api/v1/schemes",
        "match": "/api/v1/match (POST)",
    }