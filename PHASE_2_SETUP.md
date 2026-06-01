# Therapeutic Companion - Phase 2: RAG Intelligence Layer

## 🧠 Overview

Phase 2 implements a production-ready Retrieval-Augmented Generation (RAG) intelligence layer that powers empathetic therapeutic conversations. The system combines:

- **ChromaDB**: Vector store for therapeutic content retrieval
- **Sentence Transformers**: Embeddings for semantic understanding
- **Google Gemini API**: Advanced language model for response generation
- **User Journal Integration**: Personalization through user-specific context

---

## 📋 Phase 2 Components

### 1. **ingest.py** - Data Ingestion Pipeline
Handles loading, processing, and vectorizing therapeutic content.

**Features:**
- Loads CSV and JSON files from `./dataa/` directory
- Cleans and combines instruction/context and response fields
- Uses `RecursiveCharacterTextSplitter` (chunk_size=1000, overlap=100)
- Initializes ChromaDB with sentence-transformers embeddings
- Comprehensive error handling and logging

**Usage:**
```bash
# Initial ingestion
python ingest.py

# Re-ingest data (clear and rebuild)
python ingest.py --reingest

# Via UI (Settings sidebar)
# Click "🔄 Re-index Data" button in authenticated sidebar
```

### 2. **brain.py** - Therapist Engine (RAG Logic)
The core intelligence module that generates therapeutic responses.

**Core Classes:**
- `TherapistEngine`: Main RAG orchestration
  - `get_response(user_input, user_id)`: Generate personalized responses
  - `check_readiness()`: Verify system readiness

**Features:**
- Retrieves relevant therapeutic context from vector store
- Loads user-specific journal entries for personalization
- Builds enriched prompts combining retrieval + journal context
- Generates empathetic responses using Gemini API
- Maintains conversation history for multi-turn context
- User isolation: Never crosses journal data between users

**System Prompt:**
```
"You are a friendly, non-judgmental Therapist Companion. Use retrieved context 
from past professional sessions to guide your tone. If the user mentions personal 
details from their journal, acknowledge them subtly. Never give medical prescriptions. 
Focus on listening and cognitive-behavioral reflections."
```

**Usage:**
```python
from brain import initialize_engine

# Initialize engine
engine = initialize_engine(api_key="your-key")  # or use GOOGLE_API_KEY env var

# Get response
response = engine.get_response(
    user_input="I'm feeling anxious",
    user_id="username",
    conversation_history=chat_history
)

print(response["response"])  # Generated therapeutic response
```

### 3. **pages/01_Companion_Chat.py** - Chat UI (Updated)
Full-featured chat interface with RAG integration.

**Features:**
- Modern chat interface using `st.chat_message`
- Rolling chat history in Streamlit session state
- Thinking spinner during response generation
- Engine status dashboard in sidebar
- Clear chat history button
- Journal management utilities
- Crisis resource information
- Setup troubleshooting guide

**Chat Flow:**
1. User enters message
2. Message added to session history
3. Engine initializes (if needed)
4. User's journal loaded (last 5 entries)
5. Context retrieved from vector store (top 5 documents)
6. Enriched prompt built with context
7. Gemini API generates response
8. Response displayed and added to history

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

**New Phase 2 dependencies:**
- langchain==0.1.7
- chromadb==0.4.17
- sentence-transformers==2.2.2
- google-generativeai==0.3.0
- python-dotenv==1.0.0

### Step 2: Set Up Google API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key for Generative AI
3. Copy your API key

**Option A: Environment Variable**
```bash
# On Windows (PowerShell)
$env:GOOGLE_API_KEY="your-api-key-here"

# On Windows (Command Prompt)
set GOOGLE_API_KEY=your-api-key-here

# On macOS/Linux
export GOOGLE_API_KEY="your-api-key-here"
```

**Option B: .env File**
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your API key
GOOGLE_API_KEY=your-api-key-here
```

### Step 3: Prepare Therapeutic Data
Create a `./dataa/` directory with therapeutic content:

```
dataa/
├── therapy_conversations.csv
├── therapeutic_responses.json
├── coping_strategies.csv
└── mindfulness_exercises.json
```

**CSV Format:**
```csv
instruction,response
"I'm feeling anxious about work","Let's break down what's making you anxious..."
"How do I handle stress?","Here are some evidence-based stress management..."
```

**JSON Format:**
```json
[
  {
    "context": "User experiencing anxiety",
    "response": "Let's explore what's causing these anxious feelings..."
  },
  {
    "instruction": "Help with depression",
    "answer": "Depression is complex, but cognitive-behavioral approaches..."
  }
]
```

### Step 4: Ingest Data
```bash
python ingest.py
```

**Expected Output:**
```
Loading CSV: therapy_conversations.csv
Successfully loaded 100 rows from therapy_conversations.csv
Loading JSON: therapeutic_responses.json
Successfully loaded 50 items from therapeutic_responses.json
Chunking 150 documents...
Successfully chunked into 425 chunks
Initializing ChromaDB...
Added 425 documents to ChromaDB collection
ChromaDB persisted to ./vector_db

=== INGESTION COMPLETE ===
Vector store location: ./vector_db
Total chunks in vector store: 425
```

### Step 5: Run the Application
```bash
streamlit run app.py
```

### Step 6: Test the Chat
1. Navigate to "💬 Companion Chat" from sidebar
2. Type a message
3. Engine initializes with context retrieval
4. Receive empathetic, personalized response

---

## 🔒 Security & Privacy

### User Isolation
- Each user's journal data is isolated to `./user_data/{username}/journal.txt`
- RAG engine verifies `user_id` before accessing journal
- **Never** retrieves or mixes journal data across users

### Data Privacy
- Vector store contains only therapeutic content from `./dataa/`
- User conversations stored locally in session state only
- No data sent to external services except Gemini API
- All conversation data can be cleared with "Clear Chat History" button

### API Key Security
- Never commit API keys to version control
- Use .env files (in .gitignore) for local development
- Use environment variables for production deployment

---

## 📊 Architecture Diagram

```
User Input
    ↓
Streamlit Chat UI (01_Companion_Chat.py)
    ↓
Session State Management
    ↓
TherapistEngine (brain.py)
    ├─→ Vector Store Query (ChromaDB)
    │   └─→ Retrieve top 5 therapeutic contexts
    │
    ├─→ Journal Context Loading
    │   └─→ Load last 5 entries from ./user_data/{user_id}/journal.txt
    │
    └─→ Prompt Enrichment + Gemini API Call
        └─→ Generate empathetic response
            ↓
Response Display + History Update
```

---

## 🛠️ Troubleshooting

### "API Key Not Configured"
**Solution:** Set `GOOGLE_API_KEY` environment variable
```bash
$env:GOOGLE_API_KEY="your-key"
streamlit run app.py
```

### "Vector Store Not Available"
**Solution:** Run data ingestion
```bash
python ingest.py
```

### No Documents in Vector Store
**Solution:** Create `./dataa/` directory with CSV/JSON files
```bash
mkdir dataa
# Add therapeutic data files to dataa/
python ingest.py
```

### "Engine Not Ready" Error
**Solution:** Check both API key and vector store
```bash
python brain.py  # Will print readiness status
```

### "No Journal Found for User"
**Solution:** This is normal for new users. Journal created in Activities/Journal tab.

---

## 📈 Performance Considerations

### Vector Store Size
- **Small dataset** (< 100 documents): ~5-10 seconds initialization
- **Medium dataset** (100-1000 documents): ~10-30 seconds
- **Large dataset** (> 1000 documents): 30-60 seconds

### Response Generation
- Average response time: 3-8 seconds
- Dependent on document retrieval + Gemini API latency
- Use "Thinking..." spinner for UX feedback

### Optimization Tips
1. **Chunking**: Larger chunks = fewer retrievals = faster responses
2. **K-value**: Retrieving top 5 is balanced for speed/quality
3. **Embedding Model**: all-MiniLM-L6-v2 is fast but accurate
4. **API Rate Limits**: Gemini API has rate limits; monitor usage

---

## 📚 Data Schema Examples

### Therapeutic CSV
```csv
instruction,response,category,difficulty
"I'm feeling depressed","Let's talk about what's happening...","depression","beginner"
"How to manage anxiety?","Try breathing exercises...","anxiety","intermediate"
```

### Therapeutic JSON (List Format)
```json
[
  {
    "context": "User with social anxiety",
    "response": "Social anxiety is common...",
    "techniques": ["exposure", "cognitive reframing"]
  }
]
```

### Therapeutic JSON (Dict Format)
```json
{
  "mindfulness_exercise": "Body Scan Meditation",
  "description": "A guided 10-minute body scan...",
  "duration_minutes": 10
}
```

---

## 🔄 Re-indexing Data

When you add new data files to `./dataa/`:

**Method 1: Via UI**
1. Sidebar → Settings → "🔄 Re-index Data"
2. Wait for confirmation

**Method 2: Via Terminal**
```bash
python ingest.py --reingest
```

**Method 3: Programmatically**
```python
from ingest import clear_and_reingest
collection = clear_and_reingest(force=True)
```

---

## 🧪 Testing

### Test Ingest Pipeline
```bash
python ingest.py
# Check for success logs and vector store in ./vector_db/
```

### Test Therapist Engine
```bash
python brain.py
# Will perform readiness check and generate test response
```

### Test Chat UI
1. Authenticate in Streamlit
2. Navigate to Companion Chat
3. Verify engine status in sidebar
4. Send test message
5. Verify response generation

---

## 📝 System Prompt Engineering

The system prompt defines the therapeutic persona:

```
"You are a friendly, non-judgmental Therapist Companion. 
Use the retrieved context from past professional sessions to guide your tone. 
If the user mentions personal details found in their journal, 
acknowledge them subtly to show growth. 
Never give medical prescriptions. 
Focus on listening and cognitive-behavioral reflections."
```

**Customization:** Edit `SYSTEM_PROMPT` in `brain.py` to adjust:
- Tone and personality
- Therapeutic approach (CBT, ACT, Humanistic, etc.)
- Safety guidelines
- Crisis response protocols

---

## 🚀 Next Steps (Phase 3+)

- **Journal Persistence**: Save and analyze journal entries over time
- **Mood Tracking**: Track emotional patterns across conversations
- **Personalized Recommendations**: Activity suggestions based on mood
- **Multi-modal Support**: Voice conversations, progress dashboards
- **Therapist Collaboration**: Integration with professional therapists
- **Extended Context**: Store longer conversation history

---

## 📞 Support Resources

- **Google Gemini Docs**: https://ai.google.dev/
- **Langchain Docs**: https://python.langchain.com/
- **ChromaDB Docs**: https://docs.trychroma.com/
- **Streamlit Docs**: https://docs.streamlit.io/

---

## ✅ Checklist: Ready for Phase 2?

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Google API key obtained and set in environment
- [ ] Therapeutic data added to `./dataa/` directory
- [ ] Data ingested: `python ingest.py` (check for 425+ chunks)
- [ ] Vector store created: `./vector_db/` directory exists
- [ ] App running: `streamlit run app.py`
- [ ] Authenticated user logged in
- [ ] Chat responding with retrieved context
- [ ] Journal context loading (if journal exists)
- [ ] Re-index button functional in Settings

**Ready to help users with empathy and evidence! 🌿**
