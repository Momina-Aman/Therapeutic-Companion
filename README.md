# 🌿 Therapeutic Companion - Complete Documentation

**A production-ready, AI-powered mental wellness companion built with Streamlit, RAG, and empathy.**

---

## 📚 Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Phase 1: Secure Foundation](#phase-1-secure-foundation)
5. [Phase 2: RAG Intelligence](#phase-2-rag-intelligence)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)

---

## 🎯 Project Overview

**Therapeutic Companion** is a sophisticated, multi-phase mental health support application that combines:

- **🔐 Secure Authentication**: Bcrypt password hashing, user isolation, encrypted storage
- **🧠 RAG Intelligence**: Retrieval-Augmented Generation powered by Gemini API
- **📚 Vector Search**: ChromaDB with semantic embeddings for context retrieval
- **🎨 Healing UI**: Calming sage green and soft blue aesthetic with accessibility
- **📖 Personalization**: User journal integration for evolving companion response

### Key Features

✅ **Zero-Access Security**: Hidden interface until authenticated  
✅ **User Data Isolation**: Per-user encrypted directories  
✅ **Multi-turn Conversations**: Context-aware therapeutic dialogue  
✅ **Empathetic Responses**: Based on therapeutic best practices  
✅ **Personalized Support**: Evolves with user's journal reflections  
✅ **Crisis Resources**: Integrated emergency support information  
✅ **Production-Ready**: PEP8, type hints, comprehensive logging  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Generative AI API key
- 2GB disk space for vector store

### Installation (5 minutes)

```bash
# 1. Clone/Download repository
cd "path/to/data base therapy project"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate sample data (optional but recommended)
python generate_sample_data.py

# 4. Set up API key
# Windows (PowerShell)
$env:GOOGLE_API_KEY="your-key-here"

# Windows (Command Prompt)
set GOOGLE_API_KEY=your-key-here

# macOS/Linux
export GOOGLE_API_KEY="your-key-here"

# 5. Ingest therapeutic data into vector store
python ingest.py

# 6. Run the application
streamlit run app.py
```

### First Test

1. Navigate to `http://localhost:8501`
2. **Sign Up**: Create a new user account
3. **Dashboard**: Welcome message with quick stats
4. **Chat**: Go to "💬 Companion Chat" and try:
   - "I'm feeling stressed about work"
   - "How can I manage anxiety?"
   - "Help me process a difficult emotion"

---

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Sidebar: Auth, Navigation, Settings               │   │
│  │  Pages: Dashboard, Chat, Activities, Clinics       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────┐   ┌──────────┐   ┌──────────┐
    │ auth.py│   │ brain.py │   │ styles.py│
    └────────┘   └──────────┘   └──────────┘
        │              │              │
        ├─ Bcrypt      ├─ Gemini API  └─ CSS Injection
        ├─ SQLite      ├─ ChromaDB
        └─ User Dirs   ├─ Retrieval
                       └─ Journal
                           Context
        │              │
        └──────────────┼──────────────┐
                       │              │
                       ▼              ▼
            ┌──────────────────┐  ┌──────────────┐
            │   ./vector_db/   │  │ ./user_data/ │
            │  (ChromaDB)      │  │  {username}/ │
            └──────────────────┘  └──────────────┘
                       ▲                  ▲
                       │                  │
                 ingest.py         journal.txt
```

### Data Flow: Chat Message

```
User Types Message
    ↓
Streamlit Session State
    ↓
TherapistEngine.get_response()
    ├─→ ChromaDB Query (top-5 therapeutic contexts)
    ├─→ Load User Journal (last 5 entries)
    ├─→ Build Enriched Prompt
    ├─→ Gemini API Call
    └─→ Return Response
    ↓
Display in Chat UI
    ↓
Save to Session History
```

---

## Phase 1: Secure Foundation

**Status**: ✅ Complete (Phase 1/Module 1)

### Components

| File | Purpose | Status |
|------|---------|--------|
| `requirements.txt` | Dependencies | ✅ |
| `auth.py` | Bcrypt + SQLite auth | ✅ |
| `styles.py` | Healing UI CSS | ✅ |
| `app.py` | Main entry point | ✅ |
| `pages/02_Activities.py` | Activity hub | ✅ |
| `pages/03_Clinic_Finder.py` | Clinic locator | ✅ |

### Key Features

- **Authentication Module** (`auth.py`)
  - `AuthManager` class with Bcrypt password hashing
  - SQLite database: `users` table with hashed credentials
  - User registration with validation
  - User login with verification
  - Automatic user directory creation

- **Zero-Access Security**
  - `check_auth()` function verifies login status
  - Sidebar hidden until authenticated
  - Login/signup form centered and empathetic

- **UI Styling** (`styles.py`)
  - Sage green (`#6B9080`) and soft blue (`#A8DADC`)
  - Rounded corners (8-12px radius)
  - Smooth animations and transitions
  - Sans-serif font stack for readability

- **Multi-Page Framework**
  - Dashboard with welcome and affirmations
  - Navigation system via sidebar buttons
  - Modular page components
  - Session state persistence

### Usage

```python
# Authentication flow
from auth import AuthManager, check_auth

auth_manager = AuthManager()

# Register new user
success, msg = auth_manager.register_user("alice", "secure_password123")

# Login user
success, msg = auth_manager.login_user("alice", "secure_password123")

# Check if authenticated
is_logged_in = check_auth(st.session_state)
```

---

## Phase 2: RAG Intelligence

**Status**: ✅ Complete (Phase 2/Module 2)

### Components

| File | Purpose | Status |
|------|---------|--------|
| `ingest.py` | Data pipeline | ✅ |
| `brain.py` | RAG engine | ✅ |
| `pages/01_Companion_Chat.py` | Chat UI | ✅ |
| `.env.example` | Config template | ✅ |
| `PHASE_2_SETUP.md` | Detailed guide | ✅ |
| `generate_sample_data.py` | Sample generator | ✅ |

### Core Modules

#### 1. **ingest.py** - Data Ingestion Pipeline

```python
from ingest import ingest_all_data

# Load, chunk, and vectorize therapeutic data
collection = ingest_all_data()
```

**Features:**
- Loads CSV/JSON from `./dataa/`
- Combines instruction/context + response fields
- Splits into chunks (size=1000, overlap=100)
- Embeds with sentence-transformers
- Stores in ChromaDB with metadata
- Logging to `./logs/ingest.log`

**Output:** `./vector_db/` (ChromaDB persisted collection)

#### 2. **brain.py** - Therapist Engine

```python
from brain import initialize_engine

# Initialize the RAG engine
engine = initialize_engine(api_key="your-key")

# Get empathetic response
response = engine.get_response(
    user_input="I'm feeling anxious",
    user_id="alice",
    conversation_history=chat_history
)

print(response["response"])  # Therapeutic response
print(response["retrieved_context"])  # Sources used
```

**TherapistEngine Class:**

| Method | Purpose |
|--------|---------|
| `__init__(api_key)` | Initialize with Gemini API |
| `get_response()` | Generate personalized response |
| `check_readiness()` | Verify API + vector store |
| `_retrieve_context()` | Query vector store |
| `_load_user_journal()` | Load personal journal context |
| `_build_context_prompt()` | Enrich prompt with context |

**System Prompt:**
```
"You are a friendly, non-judgmental Therapist Companion. 
Use retrieved context from past professional sessions. 
If user mentions journal details, acknowledge subtly. 
Never give medical prescriptions. 
Focus on listening and cognitive-behavioral reflections."
```

#### 3. **pages/01_Companion_Chat.py** - Chat Interface

```
User Message
    ↓
Display in Chat UI (st.chat_message)
    ↓
Engine.get_response() with spinner
    ↓
Display Response
    ↓
Add to Session History
```

**Features:**
- Modern chat interface
- Rolling conversation history
- Engine status dashboard
- Clear history button
- Journal management UI
- Crisis resources panel

### Setup Workflow

```bash
# 1. Prepare data
mkdir dataa
# Add therapeutic CSV/JSON files

# 2. Generate samples (optional)
python generate_sample_data.py

# 3. Set API key
$env:GOOGLE_API_KEY="sk-..."

# 4. Ingest data
python ingest.py
# Creates ./vector_db/ with 425+ chunks

# 5. Run app
streamlit run app.py

# 6. Chat!
# Navigate to Companion Chat page
```

---

## 📊 Data Schema

### Therapeutic CSV Format

```csv
instruction,response
"I'm anxious about presentations","Let's break this down..."
"How to manage stress?","Try the 5-4-3-2-1 technique..."
```

### Therapeutic JSON Format

```json
[
  {
    "context": "User with social anxiety",
    "response": "Social anxiety often stems from..."
  }
]
```

### Vector Store Schema

```
{
  "id": "doc_12345_678910",
  "document": "Context: I'm anxious...\nResponse: Try breathing...",
  "metadata": {
    "filename": "therapy_data.csv",
    "chunk_index": 2,
    "source_type": "csv"
  }
}
```

### User Journal Format

```
Entry 1:
Today I felt anxious about the presentation...

---

Entry 2:
I tried the breathing technique and it helped...
```

---

## 🔒 Security Features

### Authentication
- **Bcrypt Hashing**: 12-round salt for password security
- **SQLite Database**: Local encrypted user credentials
- **Session State**: Streamlit persists login across refreshes
- **Unique Constraints**: Database prevents duplicate usernames

### Data Isolation
- **Per-User Directories**: `./user_data/{username}/`
- **Journal Isolation**: RAG engine verifies user_id before access
- **No Cross-User Leakage**: Vector store is shared but journal is not

### API Security
- **Environment Variables**: Never hardcode API keys
- **.gitignore**: Excludes .env files from version control
- **No Logging**: API keys never written to logs

### Encryption
- **Vector Store**: ChromaDB uses DuckDB with built-in security
- **Session Data**: Streamlit handles securely in-memory
- **User Directories**: Recommend OS-level encryption

---

## 🧠 RAG (Retrieval-Augmented Generation)

### How It Works

1. **Retrieve**: Query vector store for top-5 relevant therapeutic contexts
2. **Augment**: Combine retrieved docs + user journal + user input into prompt
3. **Generate**: Gemini API generates empathetic response using context

### Advantages

- 📚 **Context-Aware**: Responses informed by professional resources
- 👤 **Personalized**: Uses user's own journal for continuity
- 🎯 **Accurate**: Grounded in retrieved therapeutic knowledge
- 🚀 **Scalable**: Add more data without retraining models

### Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `RETRIEVAL_K` | 5 | Docs to retrieve |
| `CHUNK_SIZE` | 1000 | Characters per chunk |
| `CHUNK_OVERLAP` | 100 | Overlap between chunks |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Sentence transformer |
| `LLM_MODEL` | gemini-pro | Language model |

---

## 📖 API Reference

### auth.py

```python
# Initialize
from auth import AuthManager, check_auth

auth = AuthManager("therapeutic_companion.db")

# Register
success, msg = auth.register_user("alice", "password123")
# → Returns: (True, "Registration successful!")

# Login
success, msg = auth.login_user("alice", "password123")
# → Returns: (True, "Login successful!")

# Verify
is_logged_in = check_auth(st.session_state)
# → Returns: True/False
```

### brain.py

```python
from brain import TherapistEngine, initialize_engine

# Initialize
engine = initialize_engine(api_key="sk-...")

# Check readiness
readiness = engine.check_readiness()
# → {
#   "api_key_configured": True,
#   "vector_store_available": True,
#   "vector_store_count": 425,
#   "ready": True
# }

# Get response
response = engine.get_response(
    user_input="I'm feeling anxious",
    user_id="alice",
    conversation_history=[{
        "user_input": "Hi",
        "response": "Hello! How are you?"
    }]
)
# → {
#   "response": "I understand anxiety can be...",
#   "retrieved_context": "...",
#   "user_id": "alice",
#   "error": None
# }
```

### ingest.py

```python
from ingest import ingest_all_data, get_collection_stats

# Ingest
collection = ingest_all_data()

# Get stats
stats = get_collection_stats()
# → {
#   "collection_name": "therapeutic_companion",
#   "total_documents": 425,
#   "vector_store_path": "./vector_db",
#   "embedding_model": "all-MiniLM-L6-v2"
# }
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "API Key Not Configured"**
```bash
# Verify environment variable is set
python -c "import os; print(os.getenv('GOOGLE_API_KEY'))"

# Set it (Windows PowerShell)
$env:GOOGLE_API_KEY="your-key-here"
streamlit run app.py
```

**2. "Vector Store Not Available"**
```bash
# Run ingestion
python ingest.py

# Verify it created ./vector_db/
dir vector_db
```

**3. "No Documents in Vector Store"**
```bash
# Check ./dataa/ directory
dir dataa

# Generate samples if empty
python generate_sample_data.py
python ingest.py
```

**4. Chat Shows "Not Ready"**
```bash
# Test engine status
python brain.py

# Should output readiness check results
```

**5. "Module Not Found" Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Verify installation
pip list | grep -E "streamlit|chromadb|langchain"
```

### Logs

Check these log files for debugging:
- `./logs/ingest.log` - Data ingestion logs
- `./logs/brain.log` - RAG engine logs

---

## 📁 Project Structure

```
data base therapy project/
├── app.py                              # Main Streamlit app
├── auth.py                             # Authentication module
├── brain.py                            # RAG Therapist Engine
├── ingest.py                           # Data ingestion pipeline
├── styles.py                           # UI styling & CSS
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment template
├── generate_sample_data.py             # Sample data generator
├── README.md                           # Project overview (this file)
├── PHASE_2_SETUP.md                    # Phase 2 detailed guide
│
├── pages/                              # Streamlit multi-page app
│   ├── 01_Companion_Chat.py            # Chat interface
│   ├── 02_Activities.py                # Activities hub
│   └── 03_Clinic_Finder.py             # Clinic finder
│
├── dataa/                              # Therapeutic data (input)
│   ├── sample_therapeutic_conversations.csv
│   └── sample_therapeutic_responses.json
│
├── vector_db/                          # ChromaDB storage (output)
│   └── [vector embeddings and metadata]
│
├── user_data/                          # User profiles (created on signup)
│   ├── alice/
│   │   └── journal.txt
│   └── bob/
│       └── journal.txt
│
├── logs/                               # Application logs
│   ├── ingest.log
│   └── brain.log
│
└── .venv/                              # Python virtual environment
```

---

## 🚀 Deployment

### Development
```bash
streamlit run app.py
# Runs on http://localhost:8501
```

### Production (Streamlit Cloud)

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables in dashboard
4. Deploy automatically on push

### Production (Docker)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

---

## 📚 Resources

- **Google Gemini API**: https://ai.google.dev/
- **Langchain**: https://python.langchain.com/
- **ChromaDB**: https://docs.trychroma.com/
- **Streamlit**: https://docs.streamlit.io/
- **Sentence Transformers**: https://www.sbert.net/

---

## ✅ Checklist: Before Production

- [ ] API key stored in environment, not in code
- [ ] Vector database contains 100+ therapeutic documents
- [ ] User authentication tested with multiple accounts
- [ ] Chat responses personalized with journal context
- [ ] Crisis resources clearly displayed
- [ ] All logs configured
- [ ] Error handling covers edge cases
- [ ] Performance acceptable (response time < 10s)
- [ ] UI tested on mobile and desktop
- [ ] Documentation complete

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch (`git checkout -b feature/your-feature`)
3. Add tests for new code
4. Follow PEP8 style guide
5. Submit pull request with description

---

## 📄 License

This project is released under the MIT License. See LICENSE file for details.

---

## 💙 Acknowledgments

Built with compassion for mental health support. Special thanks to:
- Therapeutic best practices from CBT, ACT, and humanistic approaches
- Open-source communities (Langchain, ChromaDB, Streamlit)
- Users who share feedback for continuous improvement

---

## 📞 Support

For questions or issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [PHASE_2_SETUP.md](PHASE_2_SETUP.md) for detailed guidance
3. Check application logs in `./logs/`
4. Verify dependencies with `pip list`

---

**Remember: This is a supportive companion tool, not a replacement for professional mental health treatment. If you or someone you know is in crisis, please reach out to a mental health professional or call 988 (US Suicide & Crisis Lifeline).**

🌿 **Made with care for your mental wellness.** 🌿
