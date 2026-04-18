"""
NoteFlow AI — Ingestion Service
PDF upload → text extraction → character-based chunking → embedding → FAISS + MongoDB storage.
"""

import os
from datetime import datetime, timezone

import fitz  # PyMuPDF

from backend.config import CHUNK_SIZE, CHUNK_OVERLAP
from backend.database import notes_col, chunks_col, activity_col

# ── Optional dependencies (FAISS + Gemini) ──────────────
# These are imported lazily so ingestion can work in
# "extract + chunk only" mode during incremental builds.
try:
    from backend.ai.gemini_client import get_embeddings_batch
    _HAS_EMBEDDINGS = True
except Exception:
    _HAS_EMBEDDINGS = False

try:
    from backend.services.memory import add_vectors
    _HAS_FAISS = True
except Exception:
    _HAS_FAISS = False


def extract_text_from_pdf(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF file.
    Returns a list of dicts: [{"page": 1, "text": "..."}, ...]
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages


def chunk_text(pages: list[dict]) -> list[dict]:
    """
    Character-based chunking: ~800-1000 chars per chunk, 100-char overlap.
    Each chunk records its source page number.
    Returns: [{"text": "...", "page_number": 1, "chunk_index": 0}, ...]
    """
    # Concatenate all pages with page markers
    full_text = ""
    page_boundaries = []  # (start_char, page_number)
    for p in pages:
        page_boundaries.append((len(full_text), p["page"]))
        full_text += p["text"] + "\n"

    chunks = []
    start = 0
    idx = 0
    while start < len(full_text):
        end = min(start + CHUNK_SIZE, len(full_text))
        chunk_text_str = full_text[start:end].strip()

        if not chunk_text_str:
            start = end
            continue

        # Determine page number for this chunk's start position
        page_num = 1
        for boundary_start, boundary_page in reversed(page_boundaries):
            if start >= boundary_start:
                page_num = boundary_page
                break

        chunks.append({
            "text": chunk_text_str,
            "page_number": page_num,
            "chunk_index": idx,
        })
        idx += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP  # slide with overlap

    return chunks


def ingest_pdf(filename: str, pdf_bytes: bytes) -> dict:
    """
    Full ingestion pipeline:
    1. Extract text from PDF
    2. Chunk the text
    3. Embed all chunks via Gemini (if available)
    4. Store vectors in FAISS (if available) → get permanent faiss_index_ids
    5. Store chunks + metadata in MongoDB
    6. Log activity

    Returns the created note document.
    """
    # Step 1: Extract
    pages = extract_text_from_pdf(pdf_bytes)
    if not pages:
        raise ValueError("PDF contains no extractable text.")

    # Step 2: Chunk
    chunks = chunk_text(pages)
    if not chunks:
        raise ValueError("No chunks could be created from the PDF.")

    # Step 3 + 4: Embed + FAISS (optional — graceful if unavailable)
    faiss_ids = None
    if _HAS_EMBEDDINGS and _HAS_FAISS:
        try:
            chunk_texts = [c["text"] for c in chunks]
            embeddings = get_embeddings_batch(chunk_texts)
            faiss_ids = add_vectors(embeddings)
        except Exception as e:
            print(f"[WARN] Embedding/FAISS step failed, storing without vectors: {e}")
            faiss_ids = None

    # Step 5a: Create note document
    title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
    note_doc = {
        "filename": filename,
        "title": title,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
        "uploaded_at": datetime.now(timezone.utc),
        "tags": [],
    }
    result = notes_col.insert_one(note_doc)
    note_id = result.inserted_id

    # Step 5b: Create chunk documents (with faiss_index_id if available)
    chunk_docs = []
    for i, chunk in enumerate(chunks):
        doc = {
            "note_id": str(note_id),
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "page_number": chunk["page_number"],
            "char_count": len(chunk["text"]),
        }
        if faiss_ids is not None:
            doc["faiss_index_id"] = faiss_ids[i]  # PERMANENT reference — never recomputed
        chunk_docs.append(doc)
    chunks_col.insert_many(chunk_docs)

    # Step 6: Log activity
    activity_col.insert_one({
        "action": "pdf_upload",
        "note_id": str(note_id),
        "details": f"Uploaded: {filename} ({len(chunks)} chunks)",
        "timestamp": datetime.now(timezone.utc),
    })

    note_doc["_id"] = str(note_id)
    return note_doc
