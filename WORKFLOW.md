# Therapeutic Companion — How It Works (Simple Explanation)

---

## What Is This Project?

This is a **mental health support web app** that lets users:
- Chat with an AI therapist that gives real, personalized advice
- Write private journal entries
- Play relaxation mini-games
- Find mental health clinics on a map
- All behind a secure login system

Think of it like a private diary + chatbot + wellness toolkit, all in one place.

---

## The 3 Big Ideas Behind It

### 1. Your password is never stored as plain text
When you sign up, your password goes through **bcrypt** — a one-way scrambling algorithm. Even if someone hacks the database, they cannot read your password. This is the same method used by banks.

### 2. The AI knows therapy, not just general knowledge
The AI does not just guess answers. Before responding, it searches a database of **real therapeutic conversations** and finds the most relevant ones. It uses those as a guide before generating its reply. This is called **RAG (Retrieval-Augmented Generation)**.

### 3. The AI remembers your journal
Every journal entry you write is saved privately. When you chat, the AI reads your last 5 journal entries and uses them to **personalize its response** — it knows your recent mood, thoughts, and what you have been going through.

---

## Step-by-Step Workflow

```
SETUP (done once before running the app)
─────────────────────────────────────────
 1. ingest.py reads CSV and JSON files from the ./dataa/ folder
    (these files contain thousands of therapeutic Q&A conversations)

 2. Each conversation is broken into small chunks (1000 characters each)

 3. Each chunk is converted to a list of 384 numbers (a "vector embedding")
    using a model called all-MiniLM-L6-v2
    → This turns words into math so the AI can measure similarity

 4. All those number-lists are stored in ChromaDB (a vector database)
    saved to the ./vector_db/ folder on disk

 After this step, the AI has its "knowledge library" ready.
```

```
WHEN A USER VISITS THE APP
────────────────────────────
 Browser → app.py (Streamlit web server starts)

 ┌─────────────────────────────────────────────┐
 │  NOT LOGGED IN?                              │
 │  → Show login/signup page                    │
 │  Sign Up: username + password → bcrypt hash  │
 │           → save to SQLite database           │
 │           → create ./user_data/username/      │
 │  Login:   check username in SQLite            │
 │           → verify password with bcrypt       │
 │           → set session_state.logged_in = True│
 └─────────────────────────────────────────────┘

 ┌─────────────────────────────────────────────┐
 │  LOGGED IN?                                  │
 │  → Show sidebar navigation + Dashboard       │
 └─────────────────────────────────────────────┘
```

```
WHEN USER SENDS A CHAT MESSAGE
────────────────────────────────
 User types: "I feel anxious about my exam tomorrow"
         │
         ▼
 01_Companion_Chat.py receives the message
         │
         ▼
 brain.py — TherapistEngine.get_response() is called
         │
         ├─ Step 1: Convert user message to a vector (384 numbers)
         │
         ├─ Step 2: Search ChromaDB for the 5 most similar
         │          therapeutic conversations (cosine similarity)
         │          → returns: [doc1, doc2, doc3, doc4, doc5]
         │
         ├─ Step 3: Load user's last 5 journal entries from
         │          ./user_data/{username}/journal.txt
         │
         ├─ Step 4: Build enriched prompt:
         │          ┌────────────────────────────────────────┐
         │          │ === RETRIEVED THERAPEUTIC CONTEXT ===  │
         │          │ [doc1] [doc2] [doc3]                   │
         │          │ === YOUR RECENT REFLECTIONS ===        │
         │          │ [journal entry 1] [journal entry 2]    │
         │          │ User Message: I feel anxious...        │
         │          └────────────────────────────────────────┘
         │
         ├─ Step 5: Send to Google Gemini 1.5 Flash API
         │          with a system prompt that says:
         │          "You are a non-judgmental therapist companion.
         │           Use CBT, mindfulness, validation techniques."
         │
         └─ Step 6: Return AI response → display in chat UI
                    + save conversation to session history
```

```
WHEN USER WRITES A JOURNAL ENTRY
──────────────────────────────────
 02_Activities.py → Journal tab
 User writes text, sets mood slider
         │
         ▼
 Saved to ./user_data/{username}/journal.txt
 Format:
   ============================================================
   [2024-01-15 10:30:00]
   ============================================================
   Mood: 😊

   Today I felt less anxious after my walk.

 Next time user chats → brain.py reads this file
 → AI knows about this entry and can reference it
```

```
WHEN USER OPENS CLINIC FINDER
────────────────────────────────
 03_Clinic_Finder.py
         │
         ▼
 Load clinic list from clinics_data.py
 (NYC-area mental health clinics with lat/lng coordinates)
         │
         ▼
 Folium draws interactive map in browser
 Each clinic = colored marker:
   Blue   = General clinic
   Green  = Therapist
   Red    = Psychiatry
         │
         ▼
 Haversine formula filters clinics by distance from center
 (same math GPS uses to calculate distance between two points)
         │
         ▼
 Click marker → popup shows phone, email, specializations
```

```
ADMIN DASHBOARD (04_Admin_Dashboard.py)
────────────────────────────────────────
 Password protected (default: "admin")
         │
         ▼
 Shows:
   - How many users are registered (counts rows in SQLite)
   - How many documents are in ChromaDB (collection.count())
   - How many journal files exist (glob ./user_data/*/journal.txt)
   - Latency chart from logs/brain.log
   - One-click re-index button (calls ingest.py again)
```

---

## Files and What They Do

| File | Simple Explanation |
|------|--------------------|
| `app.py` | The front door — handles login, logout, page routing |
| `auth.py` | The security guard — checks passwords, creates accounts |
| `brain.py` | The AI brain — searches vector DB, reads journal, calls Gemini |
| `ingest.py` | The librarian — reads data files and builds the knowledge library |
| `styles.py` | The designer — adds the calming green/blue color theme |
| `clinics_data.py` | The directory — list of mental health clinics with coordinates |
| `logger_utils.py` | The recorder — writes structured logs without saving user names |
| `pages/00_Home.py` | Dashboard — journal count, database status, daily affirmation |
| `pages/01_Companion_Chat.py` | Chat UI — input box, chat bubbles, calls brain.py |
| `pages/02_Activities.py` | Games + Journal — breathing bubble, word scramble, diary |
| `pages/03_Clinic_Finder.py` | Map page — Folium interactive clinic map |
| `pages/04_Admin_Dashboard.py` | System monitor — only admins see this |
| `pages/05_Settings_And_Profile.py` | Account settings — export journal, change preferences |

---

## Data Storage — Where Everything Lives

```
therapeutic_companion.db   ← SQLite: usernames + bcrypt-hashed passwords
./vector_db/               ← ChromaDB: 384-dimensional vector embeddings
./user_data/
    alice/
        journal.txt        ← Alice's private journal entries only
    bob/
        journal.txt        ← Bob's private journal entries only
./dataa/
    sample_therapeutic_conversations.csv   ← training data
    sample_therapeutic_responses.json      ← training data
./logs/
    brain.log              ← AI response times and errors
    ingest.log             ← data loading logs
```

---

## The RAG Pipeline — Explained Like You're 10

Imagine you are a student studying for an exam.

**Without RAG (normal AI):**
The AI only knows what it learned during training — like a student answering from memory.

**With RAG (this project):**
1. The student (AI) has a bookshelf (ChromaDB) full of therapy notes
2. Before answering, they pull out the 5 most relevant pages from the bookshelf
3. They also read your personal diary (journal)
4. Then they write an answer using both sources

The result is more accurate, more personal, and more relevant than a generic AI response.

---

## How to Run It (Quick Version)

```powershell
# Step 1: Install packages (one time only)
pip install -r requirements.txt

# Step 2: Add your Google API key
# Open .streamlit/secrets.toml and change:
# GOOGLE_API_KEY = "paste_your_real_key_here"
# Get key free from: https://makersuite.google.com/app/apikey

# Step 3: Build the knowledge library (one time only)
python ingest.py

# Step 4: Run the app
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Summary in One Sentence

> A user logs in securely, writes private journal entries, and chats with an AI therapist that searches a vector database of therapeutic knowledge AND reads the user's own journal to give personalized, grounded mental health support.

---

*This project is not a replacement for professional mental health care.*
*Crisis support: 988 Suicide & Crisis Lifeline (call or text 988, US)*
