# NoteFlow AI — Project Exploration Summary

## 1. Application Overview

**Project Name:** NoteFlow AI  
**Purpose:** AI-powered learning assistant that transforms static notes into an intelligent, context-aware knowledge system  
**Type:** Full-stack Python/TypeScript application with dual frontends (Streamlit + Next.js)  
**Target:** Hackathon MVP — single-user, local-first, fully functional demo

### Core Features:
1. **PDF Ingestion** — Upload PDFs → extract text → chunk → embed → store in FAISS
2. **Semantic Search** — Search across all ingested notes via FAISS similarity
3. **AI Suggestions** — Summarize, simplify, and generate revision questions (Gemini-powered)
4. **Learning Planner** — Generate structured study roadmaps from user goals
5. **Understanding Score** — Gamified metric based on note interactions and AI usage
6. **Note Browser** — View, search, and explore ingested notes with linked suggestions

---

## 2. Architecture & Tech Stack

### Stack Summary:
| Component | Technology |
|-----------|-----------|
| Frontend (Primary) | **Streamlit** |
| Frontend (Web) | **Next.js** (TypeScript) |
| Backend API | **FastAPI** (Python 3.10+) |
| AI/LLM | **Google Gemini API** (`gemini-2.0-flash`) |
| Embeddings | **Gemini Embedding API** (`models/text-embedding-004`) |
| Vector DB | **FAISS** (CPU, flat index) |
| Database | **MongoDB** (local or Atlas) |
| PDF Parsing | **PyMuPDF** (`fitz`) |

### System Diagram:
```
Streamlit Frontend / Next.js Web Frontend
             ↓
        FastAPI Backend (main.py)
             ↓
    ┌────────┴────────┐
    ↓                 ↓
MongoDB          FAISS Index
(Metadata)       (Vectors)
    ↑                 ↑
    └────────┬────────┘
             ↓
        Gemini API
   (Embeddings & LLM)
```

---

## 3. Note Summarization Endpoints

### 📌 Key Finding: Three Related Endpoints

All summarization endpoints are in the **Suggestions Router** (`/api/suggest/*`) and expect `note_id` in the request body.

#### Endpoint 1: **Summarize**
- **Route:** `POST /api/suggest/summarize`
- **Request Body:** 
  ```json
  {
    "note_id": "string"
  }
  ```
- **Response:**
  ```json
  {
    "note_id": "string",
    "type": "summary",
    "content": "string"
  }
  ```
- **Implementation:** [backend/routers/suggest.py](backend/routers/suggest.py#L17-L25)
- **Service Logic:** [backend/services/suggestions.py](backend/services/suggestions.py#L33-L44)
- **Prompt:** [backend/ai/prompts.py](backend/ai/prompts.py#L5-L12)

#### Endpoint 2: **Simplify**
- **Route:** `POST /api/suggest/simplify`
- **Request Body:** Same as above (expects `note_id`)
- **Response:**
  ```json
  {
    "note_id": "string",
    "type": "simplification",
    "content": "string"
  }
  ```
- **Implementation:** [backend/routers/suggest.py](backend/routers/suggest.py#L28-L36)
- **Service Logic:** [backend/services/suggestions.py](backend/services/suggestions.py#L47-L58)

#### Endpoint 3: **Revision Questions**
- **Route:** `POST /api/suggest/revise`
- **Request Body:** Same (expects `note_id`)
- **Response:**
  ```json
  {
    "note_id": "string",
    "type": "revision_questions",
    "content": "string"
  }
  ```
- **Implementation:** [backend/routers/suggest.py](backend/routers/suggest.py#L39-L47)
- **Service Logic:** [backend/services/suggestions.py](backend/services/suggestions.py#L61-L72)

### 📌 Request Model Definition

**File:** [backend/routers/suggest.py](backend/routers/suggest.py#L7-L9)

```python
class SuggestRequest(BaseModel):
    note_id: str
```

This model is used by all three endpoints and expects a `note_id` parameter in the JSON request body.

---

## 4. The Endpoint Expecting "note_id" in Request Body

### ✅ All Three Suggestion Endpoints

The three endpoints shown above (`/api/suggest/summarize`, `/api/suggest/simplify`, `/api/suggest/revise`) all expect `note_id` in the request body via the `SuggestRequest` model.

### How It Works:

1. **Request arrives** with `{"note_id": "..."}` in JSON body
2. **Pydantic validates** using `SuggestRequest` model
3. **Service retrieves** chunks from MongoDB for that note:
   - File: [backend/services/suggestions.py](backend/services/suggestions.py#L11-L22)
   - Limits to top 3 chunks (configurable via `GEMINI_CONTEXT_CHUNKS`)
4. **Gemini API** processes the context with a system prompt + user prompt
5. **Activity logged** to MongoDB `activity_col`
6. **Result returned** with the generated content

---

## 5. Frontend Calls to Summarization Endpoints

### Frontend 1: Streamlit (Primary)

**File:** [frontend/pages/3_💡_Suggestions.py](frontend/pages/3_💡_Suggestions.py)

**How it works:**
1. User selects a note from dropdown (fetched from `/api/notes`)
2. Clicks one of three buttons: "Summarize", "Simplify", or "Revision Questions"
3. Backend endpoint is called with `note_id` in JSON body

**Code Snippet:**
```python
if col1.button("📝 Summarize", use_container_width=True, type="primary"):
    action = ("summarize", "/api/suggest/summarize", "Summary")
if col2.button("🎯 Simplify", use_container_width=True):
    action = ("simplify", "/api/suggest/simplify", "Simplification")
if col3.button("❓ Revision Questions", use_container_width=True):
    action = ("revise", "/api/suggest/revise", "Revision Questions")

if action:
    _, endpoint, label = action
    with st.spinner(f"Generating {label}..."):
        try:
            result = api_post(endpoint, json_data={"note_id": note_id})
            st.subheader(f"📋 {label}")
            st.markdown(result.get("content", "No content returned."))
        except Exception as e:
            st.error(f"Failed: {e}")
```

**API Helper:**
- File: [frontend/utils.py](frontend/utils.py#L23-L31)
- Function: `api_post(endpoint, json_data={"note_id": note_id})`
- Makes a POST request to `{BACKEND_URL}{endpoint}` with JSON body

---

### Frontend 2: Next.js Web App (Secondary)

**File:** [web/app/study/page.tsx](web/app/study/page.tsx)

**Current Implementation Note:** ⚠️ **Mismatch Detected**

The Next.js frontend uses a different request model than the backend:

```typescript
// web/app/lib/api.ts
summarize: (text: string) =>
  request<{ result: string }>('/api/suggest/summarize', {
    method: 'POST',
    body: JSON.stringify({ text }),  // ❌ sends 'text', not 'note_id'
  }),
simplify: (text: string) =>
  request<{ result: string }>('/api/suggest/simplify', {
    method: 'POST',
    body: JSON.stringify({ text }),
  }),
revise: (text: string) =>
  request<{ result: string }>('/api/suggest/revise', {
    method: 'POST',
    body: JSON.stringify({ text }),
  }),
```

**Actual Call in Study Page:**
```typescript
const text = `Note title: ${selectedNote.title}. Please ${action} the content of this note.`;
const d = await actionConfig[action].fn(text);
```

**Issue:** The Next.js app sends `{ text: "..." }` but backend expects `{ note_id: "..." }`

**Location:** [web/app/study/page.tsx](web/app/study/page.tsx#L60-L64)

---

## 6. Data Flow for Note Summarization

### Complete Flow:

```
1. Streamlit User Interface
   └─→ User selects note from /api/notes list
   └─→ User clicks "Summarize" button
       │
       └─→ 2. Streamlit Frontend (pages/3_💡_Suggestions.py)
           └─→ Calls api_post("/api/suggest/summarize", {"note_id": "..."})
               │
               └─→ 3. FastAPI Backend (main.py router registration)
                   └─→ Route: POST /api/suggest/summarize
                   └─→ Handler: summarize_note(req: SuggestRequest)
                       │
                       └─→ 4. Suggestions Service (services/suggestions.py)
                           └─→ summarize(note_id) function
                           └─→ Retrieves chunks from MongoDB via _get_note_context()
                           └─→ Limits to GEMINI_CONTEXT_CHUNKS (top 3 chunks)
                               │
                               └─→ 5. Gemini Client (ai/gemini_client.py)
                                   └─→ generate_text(system_prompt, user_prompt)
                                   └─→ Calls Google Gemini API
                                       │
                                       └─→ 6. Google Gemini API (gemini-2.0-flash)
                                           └─→ Processes context with SUMMARIZE_SYSTEM prompt
                                           └─→ Returns summary text
                                   │
                               └─→ 7. Activity Logging (MongoDB)
                                   └─→ Records action: "summarize", note_id, timestamp
                                   │
                               └─→ 8. Return Response to Frontend
                                   └─→ JSON: { "note_id": "...", "type": "summary", "content": "..." }

5. Streamlit Displays Result
   └─→ Shows summary in markdown format
```

---

## 7. File Location Map

### Backend Routes:
- **Main App Entry:** [backend/main.py](backend/main.py)
- **Suggestions Router:** [backend/routers/suggest.py](backend/routers/suggest.py)
- **Notes Router:** [backend/routers/notes.py](backend/routers/notes.py)
- **Search Router:** [backend/routers/search.py](backend/routers/search.py)
- **Planner Router:** [backend/routers/planner.py](backend/routers/planner.py)
- **Dashboard Router:** [backend/routers/dashboard.py](backend/routers/dashboard.py)
- **Ingest Router:** [backend/routers/ingest.py](backend/routers/ingest.py)

### Backend Services:
- **Suggestions Service:** [backend/services/suggestions.py](backend/services/suggestions.py) — summarize(), simplify(), generate_revision()
- **AI Prompts:** [backend/ai/prompts.py](backend/ai/prompts.py) — SUMMARIZE_SYSTEM, SIMPLIFY_SYSTEM, REVISE_SYSTEM
- **Gemini Client:** [backend/ai/gemini_client.py](backend/ai/gemini_client.py) — get_embedding(), generate_text()

### Frontend (Streamlit):
- **Main App:** [frontend/app.py](frontend/app.py)
- **Upload Page:** [frontend/pages/1_📄_Upload.py](frontend/pages/1_📄_Upload.py)
- **Explorer Page:** [frontend/pages/2_🔍_Explorer.py](frontend/pages/2_🔍_Explorer.py)
- **Suggestions Page:** [frontend/pages/3_💡_Suggestions.py](frontend/pages/3_💡_Suggestions.py) — ✅ Calls summarization endpoints
- **Planner Page:** [frontend/pages/4_🎯_Planner.py](frontend/pages/4_🎯_Planner.py)
- **Dashboard Page:** [frontend/pages/5_📊_Dashboard.py](frontend/pages/5_📊_Dashboard.py)
- **Utilities:** [frontend/utils.py](frontend/utils.py) — api_post(), api_get(), search()

### Frontend (Next.js - Web):
- **Study Page:** [web/app/study/page.tsx](web/app/study/page.tsx) — ⚠️ Uses different request format
- **API Client:** [web/app/lib/api.ts](web/app/lib/api.ts) — ⚠️ Sends { text } instead of { note_id }

---

## 8. Key Insights & Observations

### ✅ Strengths:
1. **Clean API Design** — Consistent routing pattern with `/api/suggest/*`
2. **Modular Service Layer** — Suggestions service cleanly separates API from business logic
3. **Activity Logging** — All AI suggestions are tracked in MongoDB for Understanding Score
4. **Context Management** — Limits chunks to top 3 to avoid Gemini token overflow
5. **Error Handling** — Proper HTTP exceptions with detailed error messages

### ⚠️ Issues/Mismatches:
1. **API Inconsistency** — Next.js frontend sends `{ text }` but backend expects `{ note_id }`
   - Streamlit frontend works correctly
   - Next.js frontend will fail if called
2. **Web App API Mismatch** — The web app never got updated to match the actual backend API

### 📊 Configuration:
- **Context Chunks:** Limited to 3 for Gemini (configurable via `GEMINI_CONTEXT_CHUNKS`)
- **Gemini Model:** `gemini-2.0-flash` for LLM, `models/text-embedding-004` for embeddings
- **Backend Port:** Default 8000
- **Frontend Port:** Streamlit default 8501, Next.js default 3000

---

## 9. Summary Table

| Aspect | Details |
|--------|---------|
| **Summarization Endpoints** | POST /api/suggest/summarize, /simplify, /revise |
| **Request Format** | JSON body: `{ "note_id": "string" }` |
| **Response Format** | `{ "note_id": "...", "type": "...", "content": "..." }` |
| **Backend Processing** | Retrieves top 3 chunks from MongoDB, embeds via Gemini |
| **AI Processing** | Gemini 2.0 Flash model with system + user prompts |
| **Frontend (Streamlit)** | ✅ Correctly calls endpoints with note_id |
| **Frontend (Next.js)** | ⚠️ Incorrectly sends text instead of note_id |
| **Activity Tracking** | All suggestions logged to MongoDB activity_col |
| **Vector Search** | FAISS for semantic search across all notes |

---

## 10. Next Steps (Recommendations)

1. **Fix Next.js API Client** — Update to send `note_id` instead of `text`
2. **Add Type Safety** — Ensure request models match across backends
3. **Add Tests** — Unit tests for suggestion service endpoints
4. **Documentation** — Add OpenAPI/Swagger documentation for endpoints
5. **Error Recovery** — Handle cases where note has no chunks gracefully
