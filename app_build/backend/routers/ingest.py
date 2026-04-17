"""
NoteFlow AI — Ingestion Router
POST /api/ingest/pdf
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.ingestion import ingest_pdf

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for ingestion into the knowledge base."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        note = ingest_pdf(file.filename, pdf_bytes)
        return {
            "status": "success",
            "message": f"Ingested {note['total_chunks']} chunks from {note['filename']}",
            "note": note,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
