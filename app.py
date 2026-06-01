"""
Therapeutic Companion - Main Application.

This is the main entry point for the Therapeutic Companion application.
It manages user authentication, sidebar navigation, and session state.

Phase 1/Module 1: Secure Foundation & Multi-Page Framework
"""

import streamlit as st
import os
from pathlib import Path
from auth import AuthManager, check_auth
from styles import inject_custom_css, get_centered_login_css


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Therapeutic Companion",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for calming aesthetics
inject_custom_css()


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state() -> None:
    """Initialize session state variables for the application."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = None

    if "auth_manager" not in st.session_state:
        st.session_state.auth_manager = AuthManager()

    if "page" not in st.session_state:
        st.session_state.page = "home"


initialize_session_state()

auth_manager = st.session_state.auth_manager


# ============================================================================
# AUTHENTICATION UI
# ============================================================================

def render_login_page() -> None:
    """Render the login and registration interface."""
    st.markdown(get_centered_login_css(), unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("---")
        st.markdown(
            "<h1 style='text-align: center; color: #6B9080;'>🌿 Therapeutic Companion</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align: center; color: #52796F; font-size: 1.1em;'>"
            "Your compassionate digital companion for mental wellness and self-care."
            "</p>",
            unsafe_allow_html=True
        )
        st.markdown("---")

        # Tabs for Login and Sign-up
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        # ============================
        # LOGIN TAB
        # ============================
        with tab1:
            st.subheader("Welcome Back")
            login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")

            if st.button("Login", key="login_btn", use_container_width=True):
                if login_username and login_password:
                    success, message = auth_manager.login_user(login_username, login_password)

                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both username and password.")

        # ============================
        # SIGN-UP TAB
        # ============================
        with tab2:
            st.subheader("Create Your Account")
            signup_username = st.text_input("Choose a username", key="signup_username", placeholder="At least 3 characters")
            signup_password = st.text_input("Create a password", type="password", key="signup_password", placeholder="At least 6 characters")
            signup_password_confirm = st.text_input("Confirm password", type="password", key="signup_password_confirm", placeholder="Re-enter your password")

            if st.button("Sign Up", key="signup_btn", use_container_width=True):
                if signup_password != signup_password_confirm:
                    st.error("Passwords do not match.")
                elif signup_username and signup_password:
                    success, message = auth_manager.register_user(signup_username, signup_password)

                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all fields.")

        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; font-size: 0.85em; color: #A8DADC;'>"
            "Your data is encrypted and secure. We prioritize your privacy."
            "</p>",
            unsafe_allow_html=True
        )


# ============================================================================
# AUTHENTICATED APP UI
# ============================================================================

def render_sidebar_navigation() -> None:
    """Render the sidebar navigation menu for authenticated users."""
    with st.sidebar:
        st.markdown("---")
        st.title(f"👤 {st.session_state.username}")
        st.markdown(f"**User Data Directory:** `./user_data/{st.session_state.username}/`")
        st.markdown("---")

        # Navigation menu
        st.subheader("📋 Navigation")

        if st.button("🏠 Dashboard", key="nav_home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

        if st.button("💬 Companion Chat", key="nav_chat", use_container_width=True):
            st.session_state.page = "companion_chat"
            st.rerun()

        if st.button("🎮 Activities", key="nav_activities", use_container_width=True):
            st.session_state.page = "activities"
            st.rerun()

        if st.button("🏥 Clinic Finder", key="nav_clinic", use_container_width=True):
            st.session_state.page = "clinic_finder"
            st.rerun()

        st.markdown("---")
        st.subheader("⚙️ Settings")

        if st.button("� Re-index Data", key="reindex_btn", use_container_width=True):
            st.info("Re-indexing data. Please wait...")
            try:
                from ingest import ingest_all_data
                collection = ingest_all_data()
                if collection:
                    st.success("✅ Vector database re-indexed successfully!")
                    st.info("The AI companion now has access to the latest therapeutic resources.")
                else:
                    st.warning("Re-indexing completed but no documents were found. Please check ./dataa/ directory.")
            except Exception as e:
                st.error(f"Error during re-indexing: {str(e)}")

        if st.button("�🚪 Logout", key="logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.page = "home"
            st.success("Logged out successfully. Refreshing...")
            st.rerun()


def render_dashboard() -> None:
    """Render the main dashboard page."""
    st.title(f"🌿 Welcome, {st.session_state.username}!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Sessions Completed", "0", help="Number of therapy sessions completed")

    with col2:
        st.metric("Insights Gained", "0", help="Personal insights from activities")

    with col3:
        st.metric("Days Active", "1", help="Days since account creation")

    st.markdown("---")

    st.subheader("📚 Quick Start")

    col1, col2 = st.columns(2)

    with col1:
        st.info(
            "💬 **Start Chatting**\n\n"
            "Connect with your therapeutic companion for guided conversations and support."
        )

    with col2:
        st.info(
            "🎮 **Explore Activities**\n\n"
            "Engage in games, journaling, affirmations, and mindfulness stories."
        )

    st.markdown("---")

    st.subheader("💡 Today's Affirmation")
    st.success(
        "\"You are stronger than you believe. Take it one moment at a time. 🌸\""
    )


def render_companion_chat() -> None:
    """Render the Companion Chat page (RAG placeholder)."""
    st.title("💬 Therapeutic Companion Chat")

    st.info(
        "🚧 **Coming Soon**\n\n"
        "This module will feature AI-powered therapeutic conversations "
        "using Retrieval-Augmented Generation (RAG) with professional "
        "mental health resources."
    )

    st.markdown("---")

    st.subheader("Planned Features:")
    st.markdown(
        """
        - **Empathetic AI Conversations**: Trained on therapeutic best practices
        - **Resource Integration**: Links to professional mental health materials
        - **Conversation History**: Track your journey and progress
        - **Mood Tracking**: Monitor emotional patterns over time
        - **Crisis Support**: Emergency resources and hotlines
        """
    )


def render_activities() -> None:
    """Render the Activities page with tabs."""
    st.title("🎮 Therapeutic Activities")

    st.subheader("Choose an activity that resonates with you:")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🎮 Games", "📖 Journal", "💡 Suggestions", "✨ Affirmations", "📚 Stories"]
    )

    with tab1:
        st.markdown("### Mindfulness Games")
        st.info("🚧 Coming Soon: Interactive games designed for relaxation and mindfulness.")

    with tab2:
        st.markdown("### Personal Journal")
        st.info("🚧 Coming Soon: Private journaling space to reflect on your thoughts and feelings.")
        st.text_area("Your thoughts...", height=150, disabled=True, placeholder="Journal entries will be saved here")

    with tab3:
        st.markdown("### Personalized Suggestions")
        st.info("🚧 Coming Soon: Tailored activity recommendations based on your mood and preferences.")

    with tab4:
        st.markdown("### Daily Affirmations")
        st.success(
            "✨ \"Your mental health matters. Be kind to yourself today.\" 🌟\n\n"
            "✨ \"Progress is progress, no matter how small.\" 💪\n\n"
            "✨ \"You deserve peace and happiness.\" 🌸"
        )

    with tab5:
        st.markdown("### Healing Stories")
        st.info("🚧 Coming Soon: Inspirational and therapeutic stories from the community.")


def render_clinic_finder() -> None:
    """Render the Clinic Finder page with Folium map integration."""
    st.title("🏥 Clinic Finder")

    st.info(
        "📍 **Locate Mental Health Services Near You**\n\n"
        "Find therapists, counselors, and mental health clinics in your area."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        city = st.text_input("Enter your city:", placeholder="e.g., New York, Los Angeles")
        service_type = st.selectbox(
            "Type of service:",
            ["Therapist", "Psychiatrist", "Counselor", "Mental Health Clinic"]
        )

    with col2:
        insurance = st.selectbox(
            "Insurance accepted:",
            ["Any", "Private Insurance", "Medicare", "Medicaid"]
        )
        distance = st.slider("Distance (miles):", 1, 50, 10)

    if st.button("Search Clinics", use_container_width=True):
        st.info("🚧 Folium map integration coming soon. Enter location to see nearby clinics.")

    st.markdown("---")

    st.subheader("💻 Tips for Finding a Therapist:")
    st.markdown(
        """
        1. **Verify Credentials**: Ensure the therapist is licensed in your state
        2. **Check Specializations**: Look for therapists experienced with your concerns
        3. **Consider Modality**: Different therapeutic approaches work for different people
        4. **Insurance & Cost**: Verify insurance acceptance and fees upfront
        5. **Initial Consultation**: Many therapists offer free initial consultations
        """
    )


# ============================================================================
# MAIN APP FLOW
# ============================================================================

def main() -> None:
    """Main application flow controller."""
    if not check_auth(st.session_state):
        # User is not logged in
        render_login_page()
    else:
        # User is logged in
        render_sidebar_navigation()

        # Route to the appropriate page
        if st.session_state.page == "companion_chat":
            render_companion_chat()
        elif st.session_state.page == "activities":
            render_activities()
        elif st.session_state.page == "clinic_finder":
            render_clinic_finder()
        else:
            # Default to dashboard
            render_dashboard()


if __name__ == "__main__":
    main()

