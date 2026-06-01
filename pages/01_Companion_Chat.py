"""
Companion Chat Page - RAG-Powered Therapeutic Conversations.

This page features AI-powered therapeutic conversations using
Retrieval-Augmented Generation (RAG) with ChromaDB and Gemini API.

Page: 01_Companion_Chat.py
Module: Therapeutic Companion - Phase 2
"""

import os
import streamlit as st
from auth import check_auth
from brain import initialize_engine
import logging
from pathlib import Path


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Companion Chat - Therapeutic Companion",
    page_icon="💬",
    layout="wide"
)

# Logging
logger = logging.getLogger(__name__)

# Check authentication
if not check_auth(st.session_state):
    st.error("Please log in to access this feature.")
    st.stop()


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_chat_session() -> None:
    """Initialize chat-related session state variables."""
    if "therapist_engine" not in st.session_state:
        st.session_state.therapist_engine = None
        st.session_state.engine_initialized = False

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "engine_error" not in st.session_state:
        st.session_state.engine_error = None


def get_therapist_engine():
    """
    Get or initialize the TherapistEngine.

    Returns:
        TherapistEngine instance or None if initialization fails.
    """
    if not st.session_state.engine_initialized:
        with st.spinner("Initializing Therapist Engine..."):
            try:
                # Resolve API key: env var first, then secrets.toml
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    try:
                        api_key = st.secrets.get("GOOGLE_API_KEY")
                    except Exception:
                        api_key = None
                engine = initialize_engine(api_key=api_key)

                if engine:
                    readiness = engine.check_readiness()

                    if not readiness["ready"]:
                        error_msg = (
                            "Engine not fully ready. "
                            "Please ensure:\n"
                            "1. GOOGLE_API_KEY environment variable is set\n"
                            "2. Vector store exists (run: python ingest.py)"
                        )
                        st.session_state.engine_error = error_msg
                        st.session_state.therapist_engine = None
                        return None

                    st.session_state.therapist_engine = engine
                    st.session_state.engine_initialized = True
                    return engine

                else:
                    error_msg = "Failed to initialize Therapist Engine"
                    st.session_state.engine_error = error_msg
                    return None

            except Exception as e:
                error_msg = f"Error initializing engine: {str(e)}"
                st.session_state.engine_error = error_msg
                logger.error(error_msg)
                return None

    return st.session_state.therapist_engine


# ============================================================================
# CHAT INTERFACE
# ============================================================================

def render_chat_interface() -> None:
    """Render the chat message interface."""
    # Display chat history
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"], avatar=message.get("avatar")):
                st.markdown(message["content"])

    # Chat input
    st.markdown("---")

    user_input = st.chat_input(
        "Share what's on your mind...",
        key="user_chat_input"
    )

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "avatar": "👤"
        })

        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Generate response
        engine = get_therapist_engine()

        if engine:
            with st.chat_message("assistant", avatar="🌿"):
                with st.spinner("Thinking..."):
                    try:
                        # Get response from TherapistEngine
                        response_data = engine.get_response(
                            user_input=user_input,
                            user_id=st.session_state.username,
                            conversation_history=st.session_state.chat_history
                        )

                        if response_data.get("error"):
                            st.error(f"Error: {response_data['error']}")
                            response_text = response_data.get("response", "")
                        else:
                            response_text = response_data.get("response", "")

                        # Display response
                        st.markdown(response_text)

                        # Add to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response_text,
                            "avatar": "🌿"
                        })

                    except Exception as e:
                        error_msg = f"Error generating response: {str(e)}"
                        st.error(error_msg)
                        logger.error(error_msg)

        else:
            with st.chat_message("assistant", avatar="🌿"):
                error_msg = (
                    "💙 I'm not quite ready to chat yet. "
                    "Here's what you can do:\n\n"
                    "1. **Set API Key**: Add `GOOGLE_API_KEY` to environment variables\n"
                    "2. **Prepare Data**: Place CSV/JSON files in `./dataa/` directory\n"
                    "3. **Ingest Data**: Run `python ingest.py` in terminal\n"
                    "4. **Refresh**: Come back and refresh this page\n\n"
                    "Once set up, I'll be here to provide compassionate support! 🌸"
                )
                st.info(error_msg)

                # Add to history for context
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                    "avatar": "🌿"
                })


# ============================================================================
# SIDEBAR UTILITIES
# ============================================================================

def render_sidebar_utilities() -> None:
    """Render sidebar utilities and settings."""
    with st.sidebar:
        st.markdown("---")
        st.subheader("💬 Chat Settings")

        # Clear history button
        if st.button("🗑️ Clear Chat History", key="clear_chat_btn", use_container_width=True):
            st.session_state.chat_history = []
            st.success("Chat history cleared")
            st.rerun()

        # Engine status
        st.markdown("---")
        st.subheader("⚙️ Engine Status")

        engine = get_therapist_engine()

        if engine:
            readiness = engine.check_readiness()
            col1, col2 = st.columns(2)

            with col1:
                if readiness["api_key_configured"]:
                    st.success("✅ API Key")
                else:
                    st.error("❌ API Key")

            with col2:
                if readiness["vector_store_available"]:
                    st.success("✅ Vector Store")
                else:
                    st.error("❌ Vector Store")

            with st.expander("📊 Detailed Stats"):
                st.metric("Documents in Store", readiness["vector_store_count"])
                st.code(f"Path: {readiness['vector_store_path']}", language="bash")

        else:
            st.warning("Engine not initialized")

        # Journal management
        st.markdown("---")
        st.subheader("📖 Journal")

        user_journal_path = Path(f"./user_data/{st.session_state.username}/journal.txt")

        if user_journal_path.exists():
            file_size = user_journal_path.stat().st_size
            st.info(f"Journal file size: {file_size} bytes")

            if st.button("📖 Open Journal", key="open_journal_btn", use_container_width=True):
                st.info("Journal feature coming soon in Settings page!")

        else:
            st.info("📝 No journal yet. Create one in the Activities page!")


# ============================================================================
# INFO PANELS
# ============================================================================

def render_info_panels() -> None:
    """Render informational panels about the companion."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌿 About Your Companion")
        st.markdown(
            """
            I'm here to provide supportive, empathetic conversations
            based on therapeutic best practices and personalized insights
            from your own reflections.

            **Key Features:**
            - 🧠 AI-powered therapeutic responses
            - 📚 Learned from professional resources
            - 📖 Personalized with your journal entries
            - 🔒 Completely private and encrypted
            """
        )

    with col2:
        st.markdown("### 💙 Important Notes")
        st.markdown(
            """
            **What I am:**
            - A supportive companion
            - A tool for self-reflection
            - A source of evidence-based strategies

            **What I'm not:**
            - A licensed therapist
            - A crisis hotline
            - Medical advice
            - A replacement for professional help
            """
        )

    st.markdown("---")

    with st.expander("🆘 Crisis Resources"):
        st.markdown(
            """
            ### If You're in Crisis

            **United States:**
            - **988 Suicide & Crisis Lifeline**: Call or text 988 (24/7, free)
            - **Crisis Text Line**: Text HOME to 741741

            **International:**
            - **Befrienders**: befrienders.org
            - **International Association for Suicide Prevention**: iasp.info

            **Emergency:**
            - Call 911 (US) or your local emergency number
            - Go to your nearest emergency room
            """
        )


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main() -> None:
    """Render the Companion Chat page."""
    st.title("💬 Therapeutic Companion Chat")

    st.markdown(
        "Welcome! I'm here to provide compassionate, supportive conversations. "
        "Share what's on your mind, and let's talk through it together. 🌸"
    )

    st.markdown("---")

    # Initialize session
    initialize_chat_session()

    # Render sidebar
    render_sidebar_utilities()

    # Create two columns for better layout
    chat_col, info_col = st.columns([2, 1])

    with chat_col:
        # Chat interface
        if len(st.session_state.chat_history) == 0:
            render_info_panels()

        render_chat_interface()

    with info_col:
        st.markdown("### 📌 Quick Guide")
        st.markdown(
            """
            1. Share your thoughts
            2. I'll listen and respond
            3. We'll reflect together
            4. You're never alone

            ---

            **💙 Remember**: Taking care of your mental health is important.
            You're worthy of support and compassion.
            """
        )


if __name__ == "__main__":
    main()
