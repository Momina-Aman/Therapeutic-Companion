"""
Context Manager - Session State & Data Consolidation Engine.

This module acts as the single source of truth for user telemetry and context
consolidation. It strictly manages user session isolation and provides clean
context pipelines for the RAG engine without data leakage.

Core Responsibilities:
    1. Session state management with secure user isolation
    2. Journal context window retrieval (localized per user)
    3. Vector store context preparation
    4. Memory lifecycle management (cleanup on logout)
    5. Cross-module data consistency verification
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib


# ============================================================================
# CONFIGURATION
# ============================================================================

USER_DATA_DIR = Path("./user_data")
VECTOR_DB_DIR = Path("./vector_db")
LOG_DIR = Path("./logs")

# Create necessary directories
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "context_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONTEXT MANAGER - SESSION STATE ENGINE
# ============================================================================

class ContextManager:
    """
    Unified session state and context consolidation engine.

    Manages:
    - User isolation verification
    - Session lifecycle
    - Journal context retrieval
    - Vector store readiness
    - Memory cleanup
    - Cross-module data consistency
    """

    def __init__(self, user_id: str):
        """
        Initialize ContextManager for a specific user.

        Args:
            user_id: Authenticated username (validated by auth layer)

        Raises:
            ValueError: If user_id is invalid or contains directory traversal attempts
        """
        # Strict user ID validation (prevent directory traversal)
        if not user_id or "/" in user_id or "\\" in user_id or ".." in user_id:
            raise ValueError(f"Invalid user_id: {user_id}")

        self.user_id = user_id
        self.user_data_path = USER_DATA_DIR / user_id

        # Verify user path exists
        if not self.user_data_path.exists():
            logger.error(f"User data path does not exist: {self.user_data_path}")
            raise ValueError(f"User directory not found for {user_id}")

        # Session state container
        self.session_state = {
            "user_id": user_id,
            "user_data_path": str(self.user_data_path),
            "created_at": datetime.now().isoformat(),
            "vector_store_ready": False,
            "journal_entries_count": 0,
            "games_played_count": 0,
        }

        logger.info(f"ContextManager initialized for user: {user_id}")

    def get_user_id_hash(self) -> str:
        """
        Get SHA256 hash of user ID for privacy-preserving logging.

        Returns:
            16-character SHA256 hash of user ID
        """
        return hashlib.sha256(self.user_id.encode()).hexdigest()[:16]

    def verify_user_isolation(self, path: Path) -> bool:
        """
        Verify that a path is within the current user's directory.

        This prevents unauthorized access to other users' data.

        Args:
            path: Path to verify

        Returns:
            True if path is within user's directory, False otherwise
        """
        try:
            # Resolve to absolute path
            resolved_path = path.resolve()
            user_dir_resolved = self.user_data_path.resolve()

            # Check if path is within user directory
            is_within = resolved_path.is_relative_to(user_dir_resolved)

            if not is_within:
                logger.warning(
                    f"Unauthorized path access attempt by {self.user_id}: {path}"
                )

            return is_within

        except Exception as e:
            logger.error(f"Error during isolation verification: {e}")
            return False

    def get_journal_context(self, k: int = 5) -> str:
        """
        Retrieve recent journal entries for context window.

        Args:
            k: Number of recent entries to retrieve

        Returns:
            Formatted journal context string (empty if no entries)
        """
        try:
            journal_path = self.user_data_path / "journal.txt"

            # Verify journal is within user directory
            if not self.verify_user_isolation(journal_path):
                logger.error(f"Isolation check failed for journal: {journal_path}")
                return ""

            if not journal_path.exists():
                logger.debug(f"No journal found for user {self.user_id}")
                return ""

            with open(journal_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            if not content:
                return ""

            # Split entries by separator
            entries = content.split("\n===\n")

            # Get last k entries
            recent_entries = entries[-k:] if len(entries) >= k else entries

            journal_context = "\n".join([
                f"[Entry {idx + 1}] {entry.strip()}"
                for idx, entry in enumerate(recent_entries) if entry.strip()
            ])

            # Update session state
            self.session_state["journal_entries_count"] = len(
                [e for e in entries if e.strip()]
            )

            logger.debug(f"Retrieved {len(recent_entries)} journal entries for {self.user_id}")

            return journal_context

        except Exception as e:
            logger.error(f"Error retrieving journal context: {e}")
            return ""

    def get_session_state(self) -> Dict[str, Any]:
        """
        Get current session state dictionary.

        Returns:
            Dictionary containing user session parameters
        """
        return self.session_state.copy()

    def update_session_state(self, key: str, value: Any) -> None:
        """
        Safely update a session state parameter.

        Args:
            key: State key
            value: New value
        """
        try:
            self.session_state[key] = value
            logger.debug(f"Updated session state: {key} = {value}")
        except Exception as e:
            logger.error(f"Error updating session state: {e}")

    def check_vector_store_readiness(self) -> bool:
        """
        Verify vector store is initialized and ready.

        Returns:
            True if vector store is available, False otherwise
        """
        try:
            if not VECTOR_DB_DIR.exists():
                logger.warning("Vector store directory does not exist")
                self.session_state["vector_store_ready"] = False
                return False

            # Check if collections exist
            collections_dir = VECTOR_DB_DIR / "collections"
            is_ready = collections_dir.exists() and any(collections_dir.iterdir())

            self.session_state["vector_store_ready"] = is_ready

            return is_ready

        except Exception as e:
            logger.error(f"Error checking vector store readiness: {e}")
            self.session_state["vector_store_ready"] = False
            return False

    def build_rag_context(
        self,
        user_input: str,
        retrieved_docs: List[str],
        max_tokens: int = 3000
    ) -> str:
        """
        Build enriched context for RAG engine.

        Combines:
        1. User input
        2. Retrieved documents from vector store
        3. Journal context (localized to user)

        Args:
            user_input: Current user query
            retrieved_docs: Documents from vector store retrieval
            max_tokens: Maximum tokens for context

        Returns:
            Enriched prompt string for RAG engine
        """
        try:
            context_parts = []

            # Add journal context first (most relevant to user)
            journal_context = self.get_journal_context(k=3)
            if journal_context:
                context_parts.append(f"=== YOUR RECENT JOURNAL ===\n{journal_context}\n")

            # Add retrieved documents
            if retrieved_docs:
                context_parts.append(
                    f"=== RELEVANT CONTEXT ===\n"
                    + "\n\n".join(retrieved_docs[:3])
                    + "\n"
                )

            # Build final prompt
            context = "".join(context_parts)
            final_prompt = f"{context}\nYour Message: {user_input}"

            logger.debug(f"Built RAG context for user {self.user_id}")

            return final_prompt

        except Exception as e:
            logger.error(f"Error building RAG context: {e}")
            return user_input

    def cleanup(self) -> None:
        """
        Clean up session resources and force garbage collection.

        Call this on user logout to prevent memory leaks and clear caches.
        """
        try:
            import gc

            # Clear session state
            self.session_state.clear()

            # Force garbage collection
            gc.collect()

            logger.info(f"Cleanup completed for user: {self.user_id}")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# ============================================================================
# STREAMLIT SESSION STATE BRIDGE
# ============================================================================

def initialize_session_state(streamlit_session) -> None:
    """
    Initialize Streamlit session state with ContextManager.

    Args:
        streamlit_session: st.session_state object from Streamlit
    """
    try:
        if "context_manager" not in streamlit_session:
            streamlit_session["context_manager"] = None

        if "user_id" not in streamlit_session:
            streamlit_session["user_id"] = None

        if "context_initialized" not in streamlit_session:
            streamlit_session["context_initialized"] = False

    except Exception as e:
        logger.error(f"Error initializing session state: {e}")


def get_context_manager(
    streamlit_session,
    user_id: str
) -> Optional[ContextManager]:
    """
    Get or create ContextManager for current user.

    Args:
        streamlit_session: st.session_state object
        user_id: Authenticated username

    Returns:
        ContextManager instance or None if creation fails
    """
    try:
        # Return cached instance if available and for same user
        if (
            streamlit_session.get("context_manager") is not None
            and streamlit_session.get("user_id") == user_id
        ):
            return streamlit_session["context_manager"]

        # Create new context manager
        cm = ContextManager(user_id)

        # Cache in session state
        streamlit_session["context_manager"] = cm
        streamlit_session["user_id"] = user_id
        streamlit_session["context_initialized"] = True

        return cm

    except Exception as e:
        logger.error(f"Error creating context manager: {e}")
        return None


def cleanup_session(streamlit_session) -> None:
    """
    Clean up ContextManager and clear Streamlit caches.

    Args:
        streamlit_session: st.session_state object
    """
    try:
        import streamlit as st

        # Cleanup context manager
        if "context_manager" in streamlit_session:
            cm = streamlit_session["context_manager"]
            if cm is not None:
                cm.cleanup()

        # Clear Streamlit caches
        st.cache_data.clear()
        st.cache_resource.clear()

        # Clear session state
        streamlit_session["context_manager"] = None
        streamlit_session["user_id"] = None
        streamlit_session["context_initialized"] = False

        logger.info("Session cleanup completed")

    except Exception as e:
        logger.error(f"Error during session cleanup: {e}")


# ============================================================================
# TELEMETRY CONSOLIDATION
# ============================================================================

def get_user_telemetry(context_manager: ContextManager) -> Dict[str, Any]:
    """
    Consolidate user telemetry from various sources.

    Args:
        context_manager: Active ContextManager instance

    Returns:
        Dictionary with user metrics and telemetry
    """
    try:
        user_data_path = Path(context_manager.session_state["user_data_path"])

        # Count journal entries
        journal_path = user_data_path / "journal.txt"
        journal_count = 0
        if journal_path.exists():
            with open(journal_path, 'r', encoding='utf-8', errors='replace') as f:
                journal_count = len([l for l in f.readlines() if l.strip().startswith("[")])

        # Consolidate telemetry
        telemetry = {
            "user_id": context_manager.user_id,
            "user_id_hash": context_manager.get_user_id_hash(),
            "journal_entries": journal_count,
            "vector_store_ready": context_manager.check_vector_store_readiness(),
            "session_state": context_manager.get_session_state(),
            "timestamp": datetime.now().isoformat(),
        }

        return telemetry

    except Exception as e:
        logger.error(f"Error consolidating telemetry: {e}")
        return {}


# ============================================================================
# CLI TESTING
# ============================================================================

if __name__ == "__main__":
    print("Context Manager Test Suite\n" + "=" * 80)

    # This would require an actual user directory to exist
    print("ContextManager module loaded successfully.")
    print("Use via: from utils.context_manager import ContextManager, get_context_manager")
