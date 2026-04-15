from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
import time

app = FastAPI(
    title="SaralSewa – AI Governance Copilot",
    description="CivicMatch Core: Eligibility & Readiness Engine",
    version="1.0.0",
)

# Middleware to help debug 404s and performance
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    # This will print in your terminal so you can see what URL is being hit
    print(f"Path: {request.url.path} | Status: {response.status_code} | Time: {duration:.2f}s")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CRITICAL FIX: Add the prefix here to match your frontend API_BASE
app.include_router(router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "SaralSewa Backend is Online",
        "docs": "/docs",
        "endpoints": ["/api/v1/match"]
    }