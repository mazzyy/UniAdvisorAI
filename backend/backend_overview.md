# Backend Overview for UniAdvisorAI

## 🎯 Goal
The backend powers a **study‑abroad recommendation assistant** for German university courses (DAAD).  It ingests scraped course data, creates vector embeddings, stores them in a persistent ChromaDB collection, and uses **Google Gemini** to answer user queries and extract structured information from uploaded documents.

---

## 📂 Project Layout (backend folder)
```
backend/
├─ Daad_scraper.py          # Selenium crawler → CSV files (Bachelor, Masters, PHD)
├─ document_parser.py       # PDF/DOCX parsing + Gemini extraction of structured data
├─ load_data.py             # Load CSVs into a pandas DataFrame & prepare searchable text
├─ rag_pipeline.py          # Core RAG class (embeddings, ChromaDB, Gemini answer generation)
├─ app.py                   # Flask REST API exposing /api/* endpoints
├─ chat.py                  # Simple CLI demo for the RAG pipeline
├─ requirements.txt         # Python dependencies (exact versions)
└─ backend_overview.md      # **THIS** file – high‑level documentation
```

---

## 🗂️ Data Sources & Formats
| Source | File(s) | Key Columns |
|--------|---------|------------|
| **DAAD Scraper** | `Bachelor/*.csv`, `Masters/*.csv`, `PHD/*.csv` | `course`, `institution`, `admission req`, `language req`, `deadline`, `url` |
| **Generated Metadata** (added by `load_data.py`) | – | `degree_type` (Bachelor/Masters/PhD), `source_file` (origin CSV) |

The CSVs are plain UTF‑8 text; each row represents a single course offering.

---

## 🔧 Data Processing Pipeline
1. **Scraping** (`Daad_scraper.py`) – Selenium navigates DAAD, extracts course fields, writes CSVs.
2. **Loading** (`load_data.py`) – Reads all CSVs, concatenates into a single `pandas.DataFrame`, adds `degree_type` and `source_file` columns.
3. **Searchable Text** (`prepare_course_text`) – Concatenates the most informative fields into a single string per row (course, institution, degree, admission req, language req, deadline).
4. **Embedding Generation** – `sentence‑transformers/all‑MiniLM‑L6‑v2` creates a 384‑dim vector for each searchable text.
5. **Vector Store** – ChromaDB (`./chroma_db`) persists vectors together with **metadata**:
   ```json
   {
     "course": "<title>",
     "institution": "<university>",
     "degree_type": "Bachelor|Masters|PhD",
     "url": "<link>",
     "source_file": "<csv name>"
   }
   ```
6. **RAG Query** (`DAADCourseRAG.ask`):
   - Semantic search in ChromaDB (optional `degree_type` filter).
   - Build a prompt that includes the retrieved course texts + metadata.
   - Call **Gemini‑2.0‑flash‑exp** to generate a friendly, detailed answer.
7. **Document Parsing** (`document_parser.py`):
   - Extract raw text from PDF/DOCX.
   - Prompt Gemini to return a strict JSON with fields such as `student_name`, `email`, `university`, `degree`, `cgpa`, `courses`, `skills`, etc.
   - Returned JSON is used by the front‑end to pre‑fill an application form.

---

## 📡 API Endpoints (`app.py`)
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Simple health‑check (`{"status":"ok"}`) |
| `POST`| `/api/parse-documents` | Upload PDF/DOCX → structured JSON via Gemini |
| `POST`| `/api/save-application` | Store user‑provided data in an in‑memory session dict |
| `POST`| `/api/get-recommendations` | Semantic search → returns top‑N `documents` + `metadatas` |
| `POST`| `/api/chat-with-recommendations` | Same as above but Gemini formats a natural‑language answer |

All routes have CORS enabled for the front‑end.

---

## 🛠️ How to Run the Backend (quick recap)
```powershell
# 1️⃣ Create & activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2️⃣ Install deps
pip install -r backend\requirements.txt

# 3️⃣ Set GOOGLE_API_KEY in a .env file (project root)
#    GOOGLE_API_KEY=YOUR_GEMINI_KEY

# 4️⃣ (Optional) Refresh data
python backend\Daad_scraper.py   # → CSVs
python -c "from backend.rag_pipeline import DAADCourseRAG; rag=DAADCourseRAG(); rag.load_courses_to_db(force_reload=True)"

# 5️⃣ Start Flask server
python backend\app.py
```
The server will listen on `http://127.0.0.1:5000`.

---

## 📊 What We Store as **Embeddings** & **Metadata**
- **Embedding Input** – the concatenated searchable text produced by `prepare_course_text`.  Example:
  ```
  Course: Computer Science – MSc
  Institution: Technical University of Munich
  Degree: Masters
  Admission Requirements: Bachelor degree in CS, 2.5 GPA
  Language Requirements: English (C1)
  Deadline: 15 July 2025
  ```
- **Metadata** – a lightweight dictionary attached to each vector (see table above).  It enables:
  - Filtering by `degree_type`.
  - Returning URLs and human‑readable fields in the final answer.
  - Debugging which CSV file a record originated from.

---

## 🧩 Extensibility Points
| Area | How to extend |
|------|---------------|
| **New data source** | Add another scraper, write its CSV into a new folder, update `load_all_courses()` to include it. |
| **Different embedding model** | Change `self.embedding_function` in `DAADCourseRAG.__init__` to another `SentenceTransformerEmbeddingFunction`. |
| **Switch LLM** | Replace `genai.GenerativeModel("models/gemini-2.0-flash-exp")` with another Gemini model or a different provider (adjust prompt format accordingly). |
| **Persist additional fields** | Add new keys to the `metadata` dict in `load_courses_to_db`. |
| **Front‑end integration** | Consume the `/api/*` JSON responses; they already contain the fields needed for UI rendering. |

---

## 📚 References & Helpful Links
- **Google Gemini API** – <https://ai.google.dev/gemini-api>
- **ChromaDB Docs** – <https://www.trychroma.com/docs>
- **Sentence‑Transformers** – <https://www.sbert.net>
- **Flask‑CORS** – <https://flask-cors.readthedocs.io>

---

*This file (`backend_overview.md`) is intended for developers joining the project, for documentation generation, and for quick onboarding.*
