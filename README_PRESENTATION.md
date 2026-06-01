# Therapeutic Companion — AI-Powered Mental Wellness Application

**Course Project | Databases & AI Systems**

---

## Project Overview

**Therapeutic Companion** is a production-grade, multi-phase web application that combines secure user authentication, a Retrieval-Augmented Generation (RAG) AI pipeline, and an empathetic user interface to deliver personalized mental wellness support.

The system was built in structured phases, each adding a new capability layer:

| Phase | Module | Description |
|-------|--------|-------------|
| Phase 1 | Secure Foundation | Authentication, session management, UI framework |
| Phase 2 | RAG Intelligence | Vector database, embeddings, Gemini LLM integration |
| Phase 3 | Wellness Activities | Mini-games, digital journal, clinic finder with maps |
| Phase 4 | Admin & Monitoring | System health dashboard, performance metrics, audit logging |
| Phase 5 | Settings & Profile | Journal management, data export, privacy controls |

---

## Technical Architecture

```
User Browser
     │
     ▼
Streamlit Frontend (app.py + pages/)
     │
     ├── auth.py          → SQLite + bcrypt authentication
     ├── brain.py         → RAG Therapist Engine
     ├── styles.py        → Custom CSS (sage green / soft blue theme)
     └── utils/
          └── context_manager.py  → Session isolation & data safety
               │
     ┌─────────────────────────────┐
     │                             │
     ▼                             ▼
ChromaDB Vector Store        user_data/{username}/
(./vector_db/)               journal.txt (per-user, isolated)
     │
     ▼
SentenceTransformer Embeddings
(all-MiniLM-L6-v2)
     │
     ▼
Google Gemini 1.5 Flash API
(therapeutic response generation)
```

### RAG Data Flow (how the chatbot answers)

```
User types a message
        │
        ▼
ChromaDB: retrieve top-5 relevant therapeutic documents
        │
        ▼
Load user's last 5 private journal entries
        │
        ▼
Build enriched prompt:
  [Retrieved clinical context] + [User journal] + [User message]
        │
        ▼
Gemini 1.5 Flash: generate empathetic response
        │
        ▼
Display in chat UI + save to session history
```

---

## Key Features

### Authentication & Security
- **bcrypt password hashing** (12 salt rounds) — industry-standard security
- **SQLite user database** — lightweight, local, persistent
- **Per-user data isolation** — every user's journal is locked to their directory
- **Session state management** — Streamlit keeps login persistent across page navigations
- **Directory traversal protection** — `ContextManager` validates all file paths

### RAG Intelligence Engine
- **Vector Store**: ChromaDB with cosine similarity, HNSW indexing
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors)
- **LLM**: Google Gemini 1.5 Flash with a therapeutic system prompt
- **Context Window Management**: token budgeting prevents prompt overflow
- **Multi-turn Conversation**: last 5 turns passed as history for continuity
- **Journal Personalization**: the AI references the user's own journal entries

### Data Ingestion Pipeline
- Loads CSV and JSON therapeutic datasets from `./dataa/`
- Normalizes fields: `instruction/context` + `response/answer` → unified text
- Chunks with `RecursiveCharacterTextSplitter` (chunk=1000, overlap=100)
- Embeds and stores in ChromaDB collection `therapeutic_companion`
- Re-indexable on demand from the admin dashboard

### Wellness Activities Hub
- **Breathing Bubble** — CSS-animated 4-4-4-4 box breathing exercise
- **Zen Clicker** — click-counter for releasing nervous energy
- **Word Scramble** — unscramble uplifting words (STRENGTH, HOPE, PEACE...)
- **Mood Matcher** — emoji memory card-matching game
- **Reaction Timer** — reflex speed test
- **Digital Journal** — timestamped entries, mood slider, auto-saved per user
- **Media Recommendations** — curated books & movies by mood category
- **Daily Affirmations** — 15 affirmations with display card
- **Healing Stories** — 5 short therapeutic stories

### Clinic Finder
- Folium interactive map with color-coded clinic type markers
- Haversine distance filtering (radius in miles)
- Filter by service type, insurance accepted
- Popup cards with phone, email, website, specializations
- Graceful offline fallback (no crash if map tiles unavailable)

### Admin Dashboard (password-protected)
- Registered user count, vector store document count, journal file count
- Latency trend chart (matplotlib) from structured JSON logs
- Error summary with type-counts
- One-click vector store re-indexing via subprocess
- Log file download as ZIP
- Health check across database, vector store, user data

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit 1.56 | Multi-page web UI |
| Auth | bcrypt + SQLite | Secure password hashing + user DB |
| Embeddings | sentence-transformers | Dense vector generation |
| Vector DB | ChromaDB (PersistentClient) | Semantic similarity search |
| LLM | Google Gemini 1.5 Flash | Therapeutic response generation |
| Data Pipeline | LangChain TextSplitter + pandas | Document chunking & CSV/JSON loading |
| Mapping | Folium + streamlit-folium | Interactive clinic maps |
| Logging | Python logging + JSON structured logs | Audit trails without PII |
| Testing | pytest | Unit and integration tests |

---

## Project Structure

```
Therapeutic-Companion/
├── app.py                          # Main entry point (auth + routing)
├── auth.py                         # AuthManager: bcrypt + SQLite
├── brain.py                        # TherapistEngine: RAG + Gemini
├── ingest.py                       # Data ingestion pipeline
├── styles.py                       # Custom CSS injection
├── clinics_data.py                 # NYC-area clinic dataset
├── logger_utils.py                 # Structured privacy-first logging
├── generate_sample_data.py         # Sample data generator
│
├── pages/
│   ├── 00_Home.py                  # Dashboard with metrics
│   ├── 01_Companion_Chat.py        # RAG chat interface
│   ├── 02_Activities.py            # Games, journal, affirmations
│   ├── 03_Clinic_Finder.py         # Folium map + clinic search
│   ├── 04_Admin_Dashboard.py       # System monitoring (password: admin)
│   └── 05_Settings_And_Profile.py  # Profile, journal export, privacy
│
├── utils/
│   └── context_manager.py          # Session isolation + journal pipeline
│
├── .streamlit/
│   ├── config.toml                 # Theme, server, UI config
│   └── secrets.toml                # API key (add your GOOGLE_API_KEY here)
│
├── dataa/                          # Therapeutic training data (CSV + JSON)
├── vector_db/                      # ChromaDB persisted embeddings
├── user_data/                      # Per-user journal directories
├── logs/                           # Structured application logs
└── requirements.txt                # All Python dependencies
```

---

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Google Gemini API key
# Edit .streamlit/secrets.toml and set:
# GOOGLE_API_KEY = "your_key_here"
# Get key from: https://makersuite.google.com/app/apikey

# 3. Generate and ingest therapeutic data
python generate_sample_data.py
python ingest.py

# 4. Run the application
streamlit run app.py
# Opens at: http://localhost:8501
```

---

## Security Design Decisions

| Decision | Reason |
|----------|--------|
| bcrypt with 12 rounds | Standard for password hashing; slow enough to resist brute-force |
| SQLite UNIQUE constraint on username | Database-level duplicate prevention, not just application-level |
| Per-user directories | Journal files are physically isolated, not just logically |
| Path validation in ContextManager | Prevents `../` directory traversal attacks |
| SHA256 hashing in logs | User IDs never appear in plain text in any log file |
| No API key in code | Always read from environment variable or `secrets.toml` |

---

## Limitations & Future Work

- The sample dataset has 20 entries; a production system would use thousands
- Gemini API requires internet access; an offline LLM (e.g., Ollama) would improve privacy
- Session metrics (games played, total sessions) are currently static placeholders
- Clinic data is a static NYC dataset; a real geocoding API (e.g., Google Maps) would enable true location search
- Journal deletion per individual entry is not yet implemented

---

*Built with compassion for mental health support. Not a replacement for professional care.*
*Emergency resources: 988 Suicide & Crisis Lifeline (call or text 988, US)*
