# 🧠 NoteFlow AI — Technical Specification

> **AI-Powered Learning Assistant (AI OS Layer)**
> Transforms static notes into an intelligent, context-aware knowledge system.

---

## 1. Executive Summary

NoteFlow AI is a Python-centric learning assistant that sits as an "AI OS layer" on top of a user's notes. Users upload PDFs, and the system ingests, chunks, embeds, and indexes them into a semantic memory engine (FAISS). The Gemini API powers proactive suggestions — summaries, simplifications, revision prompts, and goal-based learning roadmaps. An Understanding Score gamifies engagement by tracking note usage and AI interaction depth.

**Target**: Hackathon MVP — single-user, local-first, fully functional demo in < 48 hours.

---

## 2. Requirements

### 2.1 Functional Requirements

| ID | Feature | Description |
|----|---------|-------------|
| FR-1 | **PDF Ingestion** | Upload PDFs → extract text → chunk → embed → store in FAISS |
| FR-2 | **Memory Engine** | Semantic search across all ingested notes via FAISS similarity |
| FR-3 | **AI Suggestions** | Gemini-powered summaries, simplifications, and revision prompts |
| FR-4 | **Learning Planner** | User sets a goal → Gemini generates a structured study roadmap |
| FR-5 | **Understanding Score** | Computed metric based on note interactions and AI usage |
| FR-6 | **Note Browser** | View, search, and explore ingested notes with linked suggestions |

### 2.2 Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Single-user system (no auth required for MVP) |
| NFR-2 | Response time < 3s for AI suggestions |
| NFR-3 | Supports PDFs up to 50 pages |
| NFR-4 | All data persisted in MongoDB (survives restart) |
| NFR-5 | FAISS index persisted to disk |

---

## 3. Architecture & Tech Stack

### 3.1 Tech Stack (STRICT)

| Layer | Technology |
|-------|-----------|
| Frontend | **Streamlit** |
| Backend API | **FastAPI** (Python 3.10+) |
| AI / LLM | **Google Gemini API** (`gemini-2.0-flash`) |
| Embeddings | **Gemini Embedding API** (`models/text-embedding-004`) |
| Vector Search | **FAISS** (CPU, flat index) |
| Database | **MongoDB** (local or Atlas free tier) |
| PDF Parsing | **PyMuPDF** (`fitz`) |

### 3.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                    │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌───────────┐ │
│  │ PDF      │ │ Note      │ │ Learning │ │ Dashboard │ │
│  │ Upload   │ │ Explorer  │ │ Planner  │ │ & Score   │ │
│  └────┬─────┘ └─────┬─────┘ └────┬─────┘ └─────┬─────┘ │
└───────┼─────────────┼────────────┼──────────────┼───────┘
        │             │            │              │
        ▼             ▼            ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                       │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Ingestion    │  │ Memory       │  │ Suggestion    │  │
│  │ Module       │  │ Engine       │  │ Engine        │  │
│  │              │  │              │  │               │  │
│  │ • PDF parse  │  │ • FAISS idx  │  │ • Summaries   │  │
│  │ • Chunk text │  │ • Embed API  │  │ • Simplify    │  │
│  │ • Embed      │  │ • Similarity │  │ • Revise      │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                 │                   │          │
│  ┌──────┴─────────────────┴───────────────────┴───────┐  │
│  │              AI PIPELINE (Gemini API)              │  │
│  └────────────────────────┬──────────────────────────┘  │
│                           │                             │
│  ┌────────────────┐  ┌────┴───────────┐                 │
│  │   MongoDB      │  │   FAISS Index  │                 │
│  │   (metadata)   │  │   (vectors)    │                 │
│  └────────────────┘  └────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Data Flow

```
PDF Upload → PyMuPDF Extract → Chunking (800–1000 chars, 100-char overlap)
                                    │
                                    ▼
                          Gemini Embedding API
                                    │
                         ┌──────────┴──────────┐
                         ▼                      ▼
                   FAISS Index              MongoDB
                   (vectors)          (chunks + metadata)
                         │                      │
                         └──────────┬───────────┘
                                    ▼
                            User Query / Trigger
                                    │
                                    ▼
                         FAISS Similarity Search
                           (top-k retrieval)
                                    │
                                    ▼
                         Gemini LLM Generation
                         (context + prompt → response)
```

---

## 4. Feature Modules

### Module 1: Ingestion Service
- **Responsibility**: PDF upload → text extraction → chunking → embedding → indexing
- **Trigger**: User uploads a PDF via Streamlit
- **Chunking Strategy**: Simple character-based splitting — **800–1000 characters per chunk with 100-character overlap**. No tokenizer dependency required.
- **Process**:
  1. PyMuPDF extracts raw text per page
  2. Pages are concatenated and split into chunks (~800–1000 chars, 100-char overlap)
  3. Each chunk is embedded via Gemini Embedding API → 768-dim vector
  4. FAISS assigns a sequential integer ID (`faiss_index_id`) when `.add()` is called
  5. Chunk text + metadata + `faiss_index_id` saved to MongoDB `chunks` collection
  6. FAISS index persisted to disk after every ingestion batch

> **⚠️ FAISS ↔ MongoDB Mapping Rule**: The `faiss_index_id` stored in MongoDB is the **permanent, immutable reference** to the vector in FAISS. It is assigned once at ingestion time and never recomputed. All retrieval lookups go through this ID.

### Module 2: Memory Engine
- **Responsibility**: Semantic search and note linking
- **Trigger**: User types a query or navigates to a note
- **Process**:
  1. Query text is embedded via Gemini Embedding API → 768-dim vector
  2. FAISS returns top-5 similar chunks (`index.search(query_vector, k=5)`)
  3. FAISS returns `(distances[], faiss_index_ids[])` — use `faiss_index_ids` to lookup chunks in MongoDB
  4. MongoDB query: `chunks.find({faiss_index_id: {$in: [id1, id2, ..., id5]}})`
  5. Related notes are displayed with similarity scores
  6. **For Gemini context**: only the **top 3 chunks** (by similarity) are passed to the LLM prompt to stay within token limits

### Module 3: Suggestion Engine
- **Responsibility**: AI-generated summaries, simplifications, revision prompts
- **Trigger**: User clicks "Summarize", "Simplify", or "Generate Revision Questions" on a note
- **Process**:
  1. Retrieve the note's chunks from MongoDB
  2. Build a structured prompt with the note content
  3. Call Gemini API with the appropriate system prompt
  4. Return formatted response to the frontend

### Module 4: Learning Planner
- **Responsibility**: Goal → structured study roadmap
- **Trigger**: User inputs a learning goal (e.g., "Master Neural Networks in 2 weeks")
- **Process**:
  1. Retrieve all note titles/topics from MongoDB
  2. Build a prompt: goal + available notes context
  3. Gemini generates a week-by-week roadmap with note references
  4. Roadmap is saved to MongoDB and displayed in the UI

### Module 5: Understanding Score
- **Responsibility**: Gamified engagement metric
- **Trigger**: Computed on-demand when the dashboard loads
- **Formula**:
  ```
  raw_score = (notes_uploaded × 5) + (queries_made × 3) + (suggestions_used × 4) + (planner_interactions × 8)
  final_score = min(raw_score, 100)
  ```
  **No complex normalization** — simple additive scoring capped at 100 via `min()`.
- **Rationale**: Each action has a fixed point value. As the user interacts more, the score climbs linearly until it caps at 100. This avoids any scaling/normalization logic.
- **Storage**: Activity events logged to MongoDB `activity_log` collection

---

## 5. API Design (FastAPI Endpoints)

### 5.1 Ingestion

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ingest/pdf` | Upload and process a PDF file |
| `GET` | `/api/notes` | List all ingested notes (metadata) |
| `GET` | `/api/notes/{note_id}` | Get a specific note with all chunks |
| `DELETE` | `/api/notes/{note_id}` | Delete a note and its vectors |

### 5.2 Memory Engine

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/search` | Semantic search across all notes |
| `GET` | `/api/notes/{note_id}/related` | Get related notes for a specific note |

### 5.3 Suggestions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/suggest/summarize` | Generate summary for a note |
| `POST` | `/api/suggest/simplify` | Simplify a note's content |
| `POST` | `/api/suggest/revise` | Generate revision questions |

### 5.4 Learning Planner

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/planner/create` | Create a learning roadmap from a goal |
| `GET` | `/api/planner/{plan_id}` | Retrieve a saved plan |
| `GET` | `/api/planner` | List all plans |

### 5.5 Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/score` | Get current Understanding Score |
| `GET` | `/api/activity` | Get recent activity log |

---

## 6. Data Models (MongoDB Schemas)

### Collection: `notes`
```json
{
  "_id": "ObjectId",
  "filename": "machine_learning_notes.pdf",
  "title": "Machine Learning Notes",
  "total_pages": 12,
  "total_chunks": 34,
  "uploaded_at": "2026-04-17T10:00:00Z",
  "tags": ["ml", "supervised-learning"]
}
```

### Collection: `chunks`
```json
{
  "_id": "ObjectId",
  "note_id": "ObjectId (ref → notes)",
  "chunk_index": 0,
  "text": "Supervised learning is a type of...",
  "page_number": 1,
  "char_count": 847,
  "faiss_index_id": 42
}
```
> **Key field**: `faiss_index_id` is the integer assigned by FAISS at `.add()` time.
> It is stored once, never recomputed, and serves as the sole bridge between
> MongoDB chunk documents and FAISS vectors. Index on this field for fast lookups.

### Collection: `plans`
```json
{
  "_id": "ObjectId",
  "goal": "Master Neural Networks in 2 weeks",
  "roadmap": [
    {
      "week": 1,
      "title": "Foundations",
      "tasks": ["Read notes: Linear Algebra Basics", "Review: Perceptron chapter"],
      "linked_note_ids": ["ObjectId", "ObjectId"]
    }
  ],
  "created_at": "2026-04-17T10:00:00Z"
}
```

### Collection: `activity_log`
```json
{
  "_id": "ObjectId",
  "action": "search | summarize | simplify | revise | plan_create | pdf_upload",
  "note_id": "ObjectId (optional)",
  "details": "User searched: 'backpropagation'",
  "timestamp": "2026-04-17T10:05:00Z"
}
```

---

## 7. AI Pipeline

### 7.1 Where Gemini Is Used

| Use Case | Gemini Model | Purpose |
|----------|-------------|---------|
| Text Embedding | `text-embedding-004` | Convert chunks/queries to 768-dim vectors |
| Summarization | `gemini-2.0-flash` | Condense note content into key points |
| Simplification | `gemini-2.0-flash` | Rewrite content at a simpler reading level |
| Revision Questions | `gemini-2.0-flash` | Generate quiz-style questions from content |
| Learning Planner | `gemini-2.0-flash` | Create structured study roadmap from goal |
| Semantic Search | `text-embedding-004` + FAISS | Embed query → FAISS top-k → return matches |

### 7.2 Prompt Flow

#### Summarization Prompt
```
SYSTEM: You are a study assistant. Summarize the following study material into
concise bullet points. Focus on key concepts, definitions, and relationships.

CONTEXT:
{chunk_texts joined by \n---\n}

Provide a structured summary with headers for each major topic.
```

#### Simplification Prompt
```
SYSTEM: You are a patient tutor. Rewrite the following content so a 15-year-old
can understand it. Use analogies and simple language. Preserve accuracy.

CONTENT:
{chunk_texts}
```

#### Revision Questions Prompt
```
SYSTEM: You are an exam prep assistant. Generate 5-7 revision questions from the
content below. Mix question types: MCQ (with 4 options), short answer, and
one "explain in your own words" question.

CONTENT:
{chunk_texts}
```

#### Learning Planner Prompt
```
SYSTEM: You are a learning coach. The user wants to achieve the goal below.
Based on their available notes, create a structured week-by-week study plan.
Reference specific notes where applicable.

GOAL: {user_goal}
TIMEFRAME: {user_timeframe or "flexible"}
AVAILABLE NOTES:
{list of note titles and brief descriptions}

Output a JSON array of weekly plans with: week number, title, tasks, and
linked note titles.
```

### 7.3 Embedding + Retrieval Flow

```
1. EMBEDDING (Ingestion Time):
   text_chunk (800–1000 chars)
       │
       ▼
   Gemini text-embedding-004 → 768-dim float vector
       │
       ├──► FAISS index.add(vector) → returns faiss_index_id (sequential int)
       │
       └──► MongoDB chunks.insert({
                text, page_number, chunk_index,
                faiss_index_id,    ◄── PERSISTED, NEVER RECOMPUTED
                note_id, char_count
            })

2. RETRIEVAL (Query Time):
   user_query → Gemini text-embedding-004 → query_vector (768-dim)
                                                  │
                                                  ▼
                                   FAISS index.search(query_vector, k=5)
                                                  │
                                                  ▼
                                   Returns: distances[5], faiss_ids[5]
                                                  │
                                                  ▼
                                   MongoDB: chunks.find({faiss_index_id: {$in: faiss_ids}})
                                                  │
                                                  ▼
                                   Sort by distance → take TOP 3 chunks only
                                                  │
                                                  ▼
                                   Build Gemini prompt with 3 chunks as context
                                   (limits token usage, avoids overflow)
                                                  │
                                                  ▼
                                   Gemini LLM → Final AI response
```

> **Why top-5 retrieval but top-3 context?** FAISS retrieves 5 candidates for
> relevance ranking, but only the best 3 are injected into the Gemini prompt.
> This keeps context under ~3000 chars and avoids hitting token limits on
> `gemini-2.0-flash`.

---

## 8. Folder Structure

```
app_build/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment variables, API keys, DB URI
│   ├── database.py              # MongoDB connection + collections
│   │
│   ├── models/
│   │   ├── note.py              # Note & Chunk Pydantic models
│   │   ├── plan.py              # Learning Plan models
│   │   └── activity.py          # Activity log models
│   │
│   ├── routers/
│   │   ├── ingest.py            # /api/ingest/* endpoints
│   │   ├── notes.py             # /api/notes/* endpoints
│   │   ├── search.py            # /api/search endpoint
│   │   ├── suggest.py           # /api/suggest/* endpoints
│   │   ├── planner.py           # /api/planner/* endpoints
│   │   └── dashboard.py         # /api/score, /api/activity endpoints
│   │
│   ├── services/
│   │   ├── ingestion.py         # PDF parse → chunk → embed → index
│   │   ├── memory.py            # FAISS operations (add, search, persist)
│   │   ├── suggestions.py       # Gemini prompt builders + API calls
│   │   ├── planner.py           # Goal → roadmap generation
│   │   └── scoring.py           # Understanding Score computation
│   │
│   ├── ai/
│   │   ├── gemini_client.py     # Gemini API wrapper (embed + generate)
│   │   └── prompts.py           # All prompt templates
│   │
│   ├── faiss_store/
│   │   └── index.faiss          # Persisted FAISS index (generated)
│   │
│   └── requirements.txt         # Python dependencies
│
├── frontend/
│   ├── app.py                   # Streamlit main app (multi-page)
│   ├── pages/
│   │   ├── 1_📄_Upload.py       # PDF upload page
│   │   ├── 2_🔍_Explorer.py     # Note browser + semantic search
│   │   ├── 3_💡_Suggestions.py  # AI suggestions interface
│   │   ├── 4_🎯_Planner.py      # Learning goal planner
│   │   └── 5_📊_Dashboard.py    # Understanding Score dashboard
│   └── utils.py                 # API client helpers
│
├── .env.example                 # Template for environment variables
├── docker-compose.yml           # MongoDB + backend + frontend (optional)
└── README.md                    # Setup and run instructions
```

---

## 9. State Management & Data Flow

```
┌──────────────┐     HTTP/JSON      ┌──────────────┐
│  Streamlit   │ ◄────────────────► │   FastAPI     │
│  (Frontend)  │   requests via     │   (Backend)   │
│              │   `requests` lib   │               │
└──────────────┘                    └───────┬───────┘
                                            │
                                    ┌───────┴───────┐
                                    ▼               ▼
                              ┌──────────┐   ┌───────────┐
                              │ MongoDB  │   │   FAISS   │
                              │ (data)   │   │ (vectors) │
                              └──────────┘   └───────────┘
```

- **Streamlit** makes HTTP calls to FastAPI using `requests` library
- **FastAPI** is the single source of truth — all logic runs here
- **MongoDB** stores all structured data (notes, chunks, plans, activity)
- **FAISS** stores only vectors; the integer ID maps to `faiss_index_id` in MongoDB `chunks`
- **No session state complexity** — Streamlit pages are stateless, backed by API calls

---

## 10. Demo Flow (Step-by-Step User Journey)

### 🎬 Live Demo Script (~5 minutes)

**Step 1 — Upload (30s)**
> User opens the app → navigates to **📄 Upload** → uploads a PDF ("Neural Networks 101.pdf")
> System shows: ✅ "12 pages parsed, 34 chunks created, indexed into memory."

**Step 2 — Explore & Search (60s)**
> User navigates to **🔍 Explorer** → sees all uploaded notes listed
> Types: *"How does backpropagation work?"*
> System returns top 3 relevant chunks with similarity scores + source pages

**Step 3 — AI Suggestions (60s)**
> User clicks on a note → clicks **"Summarize"**
> AI returns structured bullet-point summary
> User clicks **"Simplify"** → gets an ELI15 version
> User clicks **"Generate Revision Questions"** → gets 5 quiz questions (MCQ + short answer)

**Step 4 — Learning Planner (60s)**
> User navigates to **🎯 Planner** → enters goal: *"Master Neural Networks in 2 weeks"*
> AI generates a week-by-week roadmap:
> - Week 1: Perceptrons, Activation Functions (links to uploaded notes)
> - Week 2: Backpropagation, CNNs, Practice Problems

**Step 5 — Understanding Score (30s)**
> User navigates to **📊 Dashboard**
> Sees their Understanding Score: **72/100**
> Breakdown: 5 notes uploaded, 8 searches, 3 summaries generated, 1 plan created
> Activity timeline shows recent interactions

---

## 11. Key Dependencies

```
# requirements.txt
fastapi==0.115.*
uvicorn==0.34.*
pymongo==4.12.*
pymupdf==1.25.*       # PyMuPDF (import fitz)
faiss-cpu==1.11.*
google-genai==1.*      # Gemini SDK
python-multipart       # File upload support
python-dotenv          # .env file loading
streamlit==1.45.*
requests               # Streamlit → FastAPI HTTP calls
```

---

## 12. Environment Variables

```env
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=noteflow_ai
FAISS_INDEX_PATH=./faiss_store/index.faiss
BACKEND_URL=http://localhost:8000
```

---

*Document Version: 1.1 | Author: Product Manager (AI Agent) | Date: 2026-04-17 | Revision: Applied PM feedback — char-based chunking, explicit FAISS↔MongoDB mapping, simplified scoring, context-limited Gemini calls*
