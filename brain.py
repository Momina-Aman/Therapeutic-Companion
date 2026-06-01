"""
Therapeutic Engine - RAG-Powered Response Generation.

This module implements the intelligence layer using:
1. ChromaDB vector store for retrieval
2. Google Gemini API for response generation
3. Journal context injection for personalization

Core Classes:
    - TherapistEngine: Main RAG orchestration engine
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
import google.generativeai as genai


# ============================================================================
# CONFIGURATION
# ============================================================================

# Directories
VECTOR_DB_DIR = Path("./vector_db")
USER_DATA_DIR = Path("./user_data")
LOG_DIR = Path("./logs")

# Create necessary directories
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "brain.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ChromaDB settings
CHROMA_SETTINGS = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=str(VECTOR_DB_DIR),
    anonymized_telemetry=False
)

# RAG configuration
RETRIEVAL_K = 5  # Number of documents to retrieve
JOURNAL_ENTRIES_K = 5  # Number of recent journal entries to include
MAX_CONTEXT_TOKENS = 3000  # Maximum tokens for retrieved context
GEMINI_MAX_TOKENS = 32000  # Gemini-pro context window
RESERVED_TOKENS = 2000  # Reserve tokens for response generation

# System prompt for the therapeutic companion
SYSTEM_PROMPT = """You are a friendly, non-judgmental Therapist Companion. Your role is to provide empathetic, supportive conversations based on therapeutic best practices.

Guidelines:
1. Use the retrieved context from past professional sessions to guide your tone and approach
2. If the user mentions personal details found in their journal, acknowledge them subtly to show growth and continuity
3. Never give medical prescriptions or clinical diagnoses
4. Focus on listening, validation, and cognitive-behavioral reflections
5. Ask clarifying questions to better understand the user's perspective
6. Celebrate small wins and progress
7. Be warm, authentic, and genuinely interested in their wellbeing
8. If they mention crisis or self-harm, provide crisis resources and encourage professional help
9. Remember previous conversation context to show continuity
10. Use evidence-based therapeutic techniques (CBT, mindfulness, validation, etc.)

Important: This is a supportive tool, not a replacement for professional mental health treatment. If the user is in crisis, always recommend they contact a mental health professional or crisis line."""


# ============================================================================
# THERAPIST ENGINE
# ============================================================================

class TherapistEngine:
    """
    RAG-powered therapeutic companion engine.

    Combines ChromaDB retrieval with Gemini API for empathetic responses.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the TherapistEngine.

        Args:
            api_key: Google Generative AI API key. If None, uses GOOGLE_API_KEY env var.

        Raises:
            ValueError: If API key is not provided and env var not set.
        """
        # Initialize Gemini API
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Google Generative AI API key not found. "
                "Provide it as an argument or set GOOGLE_API_KEY environment variable."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            system_instruction=SYSTEM_PROMPT
        )

        logger.info("Gemini API initialized successfully")

        # Initialize ChromaDB
        self.collection = self._initialize_retriever()

    def _initialize_retriever(self) -> Optional[chromadb.Collection]:
        """
        Initialize ChromaDB retriever.

        Returns:
            ChromaDB collection or None if vector store doesn't exist.
        """
        try:
            if not VECTOR_DB_DIR.exists():
                logger.warning(f"Vector DB directory {VECTOR_DB_DIR} not found.")
                logger.info("Please run 'python ingest.py' to initialize the vector store.")
                return None

            client = chromadb.Client(CHROMA_SETTINGS)
            collection = client.get_or_create_collection(
                name="therapeutic_companion",
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"ChromaDB collection loaded with {collection.count()} documents")
            return collection

        except Exception as e:
            logger.error(f"Error initializing retriever: {e}")
            return None

    @staticmethod
    def _estimate_token_count(text: str) -> int:
        """
        Estimate token count for text using simple heuristic.

        Approximation: ~1 token per 4 characters (rough estimate for English).
        For accurate counting, use tiktoken or Google's official counter.

        Args:
            text: Text to estimate tokens for.

        Returns:
            Estimated token count.
        """
        # Simple heuristic: split by whitespace and punctuation
        import re
        tokens = re.findall(r'\b\w+\b|[.,!?;:\'-"]', text)
        return len(tokens)

    def _trim_context_by_tokens(
        self,
        context_docs: List[str],
        max_tokens: int = MAX_CONTEXT_TOKENS
    ) -> List[str]:
        """
        Trim context documents to fit within token budget.

        Args:
            context_docs: List of context documents.
            max_tokens: Maximum tokens allowed for context.

        Returns:
            Trimmed list of context documents that fit within token budget.
        """
        trimmed_docs = []
        total_tokens = 0

        for doc in context_docs:
            doc_tokens = self._estimate_token_count(doc)

            if total_tokens + doc_tokens <= max_tokens:
                trimmed_docs.append(doc)
                total_tokens += doc_tokens
            else:
                # Try to fit a partial document if it's the first one
                if not trimmed_docs and doc_tokens > max_tokens:
                    # Truncate doc to fit
                    words = doc.split()
                    partial_doc = ""

                    for word in words:
                        if self._estimate_token_count(partial_doc + " " + word) <= max_tokens:
                            partial_doc += " " + word if partial_doc else word
                        else:
                            break

                    if partial_doc:
                        trimmed_docs.append(partial_doc + "...")

                break

        logger.debug(
            f"Trimmed context from {len(context_docs)} docs "
            f"({self._estimate_token_count(''.join(context_docs))} tokens) "
            f"to {len(trimmed_docs)} docs ({total_tokens} tokens)"
        )

        return trimmed_docs

    def _retrieve_context(self, query: str, k: int = RETRIEVAL_K) -> List[str]:
        """
        Retrieve relevant therapeutic context from vector store.

        Args:
            query: User input/question.
            k: Number of documents to retrieve.

        Returns:
            List of retrieved context documents.
        """
        if not self.collection:
            logger.warning("Vector store not available. No context retrieved.")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )

            context_docs = []
            if results and results["documents"]:
                for docs in results["documents"]:
                    context_docs.extend(docs)

            logger.debug(f"Retrieved {len(context_docs)} context documents for query")
            return context_docs

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def _load_user_journal(self, user_id: str, k: int = JOURNAL_ENTRIES_K) -> str:
        """
        Load recent journal entries from user's personal data directory.

        Args:
            user_id: Username/user identifier.
            k: Number of recent entries to load.

        Returns:
            Formatted journal context or empty string if no journal found.
        """
        try:
            journal_path = USER_DATA_DIR / user_id / "journal.txt"

            if not journal_path.exists():
                logger.debug(f"No journal found for user {user_id}")
                return ""

            with open(journal_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content:
                return ""

            # Split entries by common separators
            entries = content.split("\n---\n")  # Common entry separator

            # Get last k entries
            recent_entries = entries[-k:] if len(entries) >= k else entries

            journal_context = "\n".join([
                f"Journal Entry {idx + 1}:\n{entry.strip()}"
                for idx, entry in enumerate(recent_entries)
            ])

            logger.debug(f"Loaded {len(recent_entries)} journal entries for user {user_id}")
            return journal_context

        except Exception as e:
            logger.error(f"Error loading journal for user {user_id}: {e}")
            return ""

    def _build_context_prompt(
        self,
        user_input: str,
        user_id: str
    ) -> Tuple[str, str]:
        """
        Build an enriched context prompt combining retrieval and journal context.

        Respects token limits to prevent context window overflow.

        Args:
            user_input: User's message.
            user_id: Username for journal isolation.

        Returns:
            Tuple of (enriched_prompt, retrieved_context) for transparency.
        """
        # Retrieve therapeutic context
        retrieved_docs = self._retrieve_context(user_input)

        # Trim to token budget
        retrieved_docs = self._trim_context_by_tokens(
            retrieved_docs,
            max_tokens=int(MAX_CONTEXT_TOKENS * 0.6)  # Use 60% for retrieval
        )

        # Load user's journal
        journal_context = self._load_user_journal(user_id)

        # Build the enriched prompt
        context_parts = []

        if retrieved_docs:
            context_parts.append(
                "=== RETRIEVED THERAPEUTIC CONTEXT ===\n" +
                "\n\n".join(retrieved_docs[:3]) +  # Use top 3 for clarity
                "\n================================\n"
            )

        if journal_context:
            context_parts.append(
                "=== YOUR RECENT REFLECTIONS ===\n" +
                journal_context +
                "\n================================\n"
            )

        if context_parts:
            enriched_prompt = (
                "".join(context_parts) +
                f"\nUser Message: {user_input}"
            )
        else:
            enriched_prompt = user_input

        retrieved_context = "\n\n".join(retrieved_docs) if retrieved_docs else ""

        return enriched_prompt, retrieved_context

    def get_response(
        self,
        user_input: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a therapeutic response using RAG.

        Args:
            user_input: User's message.
            user_id: Username for journal isolation and personalization.
            conversation_history: Previous conversation turns for context.

        Returns:
            Dictionary containing:
                - response: Generated therapeutic response
                - retrieved_context: Documents used for retrieval
                - user_id: User identifier (for verification)
                - error: Error message if applicable
        """
        try:
            # Validate API and vector store readiness
            if not self.api_key:
                error_msg = "API key not configured."
                logger.error(error_msg)
                return {
                    "response": "I apologize, but I'm not ready to chat yet. Please configure the API key.",
                    "error": error_msg,
                    "user_id": user_id
                }

            if not self.collection:
                logger.warning("Vector store not available. Using Gemini without context.")

            # Build enriched prompt with context
            enriched_prompt, retrieved_context = self._build_context_prompt(
                user_input, user_id
            )

            # Build message history for multi-turn conversation
            messages = []

            if conversation_history:
                for turn in conversation_history[-5:]:  # Last 5 turns for context
                    messages.append({
                        "role": "user",
                        "parts": turn.get("user_input", "")
                    })
                    messages.append({
                        "role": "model",
                        "parts": turn.get("response", "")
                    })

            # Add current user input
            messages.append({
                "role": "user",
                "parts": enriched_prompt
            })

            # Generate response
            logger.info(f"Generating response for user {user_id}...")

            response = self.model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1024,
                    temperature=0.7,
                    top_p=0.95,
                )
            )

            generated_text = response.text if response else "I'm having trouble generating a response. Please try again."

            logger.info(f"Response generated successfully for user {user_id}")

            return {
                "response": generated_text,
                "retrieved_context": retrieved_context,
                "user_id": user_id,
                "error": None
            }

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)

            return {
                "response": "I apologize, but I encountered an error. Please try again in a moment.",
                "error": error_msg,
                "user_id": user_id
            }

    def check_readiness(self) -> Dict[str, Any]:
        """
        Check if the engine is ready to generate responses.

        Returns:
            Dictionary with readiness status and details.
        """
        return {
            "api_key_configured": bool(self.api_key),
            "vector_store_available": self.collection is not None,
            "vector_store_count": self.collection.count() if self.collection else 0,
            "vector_store_path": str(VECTOR_DB_DIR),
            "user_data_path": str(USER_DATA_DIR),
            "ready": bool(self.api_key and self.collection)
        }

    def cleanup(self) -> None:
        """
        Clean up resources and force garbage collection.

        Call this on user logout to free memory and caches.
        """
        try:
            import gc

            # Clear collection reference
            self.collection = None

            # Force garbage collection
            gc.collect()

            logger.info("TherapistEngine cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# ============================================================================
# INITIALIZATION HELPER
# ============================================================================

def initialize_engine(api_key: Optional[str] = None) -> Optional[TherapistEngine]:
    """
    Initialize and return a TherapistEngine instance.

    Args:
        api_key: Optional Google API key.

    Returns:
        TherapistEngine instance or None if initialization fails.
    """
    try:
        logger.info("Initializing Therapist Engine...")
        engine = TherapistEngine(api_key=api_key)

        readiness = engine.check_readiness()
        logger.info(f"Engine readiness check: {readiness}")

        if not readiness["ready"]:
            logger.warning("Engine not fully ready.")
            if not readiness["vector_store_available"]:
                logger.warning("Vector store not available. Run 'python ingest.py' first.")

        return engine

    except Exception as e:
        logger.error(f"Failed to initialize engine: {e}")
        return None


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    import sys

    # Initialize engine
    engine = initialize_engine()

    if not engine:
        print("Failed to initialize engine.")
        sys.exit(1)

    # Check readiness
    readiness = engine.check_readiness()
    print("\n" + "=" * 80)
    print("THERAPIST ENGINE READINESS CHECK")
    print("=" * 80)
    for key, value in readiness.items():
        print(f"{key}: {value}")
    print("=" * 80)

    # Test response generation
    if readiness["ready"]:
        print("\nGenerating test response...")
        test_input = "I'm feeling stressed about work today. Can you help me?"
        response = engine.get_response(test_input, user_id="test_user")

        print("\n" + "=" * 80)
        print("TEST RESPONSE")
        print("=" * 80)
        print(f"Input: {test_input}")
        print(f"\nResponse:\n{response['response']}")
        if response.get("error"):
            print(f"\nError: {response['error']}")
        print("=" * 80)
    else:
        print("\nEngine not ready for testing. Please configure API key and run ingest.py")
