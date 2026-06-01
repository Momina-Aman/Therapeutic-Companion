"""
Home Page - Onboarding Experience & Dashboard.

This is the landing page after successful login. It provides:
- Dynamic greeting based on system time
- Progress metrics dashboard
- Quick-launch dock for navigation
- System status indicators
- Personalized welcome experience

Author: Therapeutic Companion Team
Version: 1.0.0
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Import utilities
try:
    from utils.context_manager import get_context_manager, ContextManager
except ImportError:
    st.error("Context manager not found. Please ensure utils/context_manager.py exists.")
    st.stop()

try:
    from styles import inject_custom_css
except ImportError:
    st.error("Styles module not found.")
    st.stop()


# ============================================================================
# CONFIGURATION
# ============================================================================

USER_DATA_DIR = Path("./user_data")
VECTOR_DB_DIR = Path("./vector_db")

# Color scheme from styles
PRIMARY_GREEN = "#6B9080"
SOFT_BLUE = "#A8DADC"
LIGHT_SAGE = "#E8F5F0"
ACCENT_GREEN = "#52796F"
TEXT_DARK = "#2C3E50"


# ============================================================================
# GREETING SYSTEM
# ============================================================================

def get_dynamic_greeting() -> tuple[str, str]:
    """
    Generate a dynamic greeting based on current system time.

    Returns:
        Tuple of (greeting_text, emoji)
    """
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good Morning ☀️", "Start your day with intention"
    elif 12 <= current_hour < 17:
        return "Good Afternoon 🌤️", "Take a moment for yourself"
    elif 17 <= current_hour < 21:
        return "Good Evening 🌅", "Reflect on your day"
    else:
        return "Good Night 🌙", "Rest well and be kind to yourself"


def render_greeting_card(user_id: str) -> None:
    """
    Render dynamic greeting card with user name.

    Args:
        user_id: Authenticated username
    """
    greeting, tagline = get_dynamic_greeting()

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {LIGHT_SAGE} 0%, {SOFT_BLUE} 100%);
        padding: 40px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(107, 144, 128, 0.15);
    ">
        <h1 style="color: {ACCENT_GREEN}; margin: 0; font-size: 2.5em;">
            {greeting}
        </h1>
        <p style="color: {TEXT_DARK}; margin: 10px 0 0 0; font-size: 1.1em;">
            Welcome back, <strong>{user_id}</strong>
        </p>
        <p style="color: {TEXT_DARK}; margin: 5px 0 0 0; font-size: 0.95em; opacity: 0.8;">
            {tagline}
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# PROGRESS METRICS
# ============================================================================

def get_user_metrics(user_id: str) -> Dict[str, Any]:
    """
    Aggregate user progress metrics from various sources.

    Args:
        user_id: Username

    Returns:
        Dictionary with user metrics
    """
    try:
        user_data_path = USER_DATA_DIR / user_id
        metrics = {
            "journal_entries": 0,
            "games_played": 0,
            "vector_db_synced": False,
            "total_sessions": 0,
        }

        # Count journal entries
        journal_path = user_data_path / "journal.txt"
        if journal_path.exists():
            with open(journal_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                metrics["journal_entries"] = len([l for l in content.split("\n") if l.startswith("[")])

        # Check vector DB status
        metrics["vector_db_synced"] = VECTOR_DB_DIR.exists() and any(
            (VECTOR_DB_DIR / "collections").glob("*") if (VECTOR_DB_DIR / "collections").exists() else []
        )

        return metrics

    except Exception as e:
        st.warning(f"Error retrieving metrics: {e}")
        return {
            "journal_entries": 0,
            "games_played": 0,
            "vector_db_synced": False,
            "total_sessions": 0,
        }


def render_metrics_panel(metrics: Dict[str, Any]) -> None:
    """
    Render progress metrics dashboard.

    Args:
        metrics: Dictionary with user metrics
    """
    st.subheader("Your Progress at a Glance")

    # Create 4-column layout for key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📔 Journal Entries",
            value=metrics["journal_entries"],
            delta="entries recorded",
            delta_color="off"
        )

    with col2:
        st.metric(
            label="🎮 Games Played",
            value=metrics["games_played"],
            delta="wellness activities",
            delta_color="off"
        )

    with col3:
        db_status = "✅ Synced" if metrics["vector_db_synced"] else "⏳ Syncing"
        st.metric(
            label="🗄️ Vector Database",
            value=db_status,
            delta="knowledge base",
            delta_color="off"
        )

    with col4:
        st.metric(
            label="📊 Total Sessions",
            value=metrics["total_sessions"],
            delta="active sessions",
            delta_color="off"
        )

    # Add progress visualization
    st.markdown("---")

    # Goal-based progress bars
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Weekly Journal Goal**")
        journal_goal = min(metrics["journal_entries"] / 7 * 100, 100)
        st.progress(journal_goal / 100)
        st.caption(f"{metrics['journal_entries']} of 7 entries this week")

    with col2:
        st.write("**Wellness Check-ins**")
        game_goal = min(metrics["games_played"] / 5 * 100, 100)
        st.progress(game_goal / 100)
        st.caption(f"{metrics['games_played']} of 5 activities completed")


# ============================================================================
# QUICK LAUNCH DOCK
# ============================================================================

def render_quick_launch_dock() -> None:
    """
    Render quick-launch navigation dock for primary features.
    """
    st.subheader("Quick Launch")

    dock_col1, dock_col2, dock_col3, dock_col4 = st.columns(4)

    with dock_col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {SOFT_BLUE} 0%, {PRIMARY_GREEN} 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <h3 style="color: white; margin: 0; font-size: 2em;">💬</h3>
            <p style="color: white; margin: 10px 0 0 0; font-weight: 500;">Companion Chat</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Open Chat", key="btn_chat", use_container_width=True):
            st.session_state.page = "01_Companion_Chat"
            st.rerun()

    with dock_col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {LIGHT_SAGE} 0%, {SOFT_BLUE} 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <h3 style="color: white; margin: 0; font-size: 2em;">🎮</h3>
            <p style="color: white; margin: 10px 0 0 0; font-weight: 500;">Activities Hub</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Explore Activities", key="btn_activities", use_container_width=True):
            st.session_state.page = "02_Activities"
            st.rerun()

    with dock_col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {ACCENT_GREEN} 0%, {PRIMARY_GREEN} 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <h3 style="color: white; margin: 0; font-size: 2em;">🏥</h3>
            <p style="color: white; margin: 10px 0 0 0; font-weight: 500;">Clinic Finder</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Find Clinics", key="btn_clinics", use_container_width=True):
            st.session_state.page = "03_Clinic_Finder"
            st.rerun()

    with dock_col4:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {PRIMARY_GREEN} 0%, {ACCENT_GREEN} 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <h3 style="color: white; margin: 0; font-size: 2em;">⚙️</h3>
            <p style="color: white; margin: 10px 0 0 0; font-weight: 500;">Settings</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Manage Settings", key="btn_settings", use_container_width=True):
            st.session_state.page = "05_Settings_And_Profile"
            st.rerun()


# ============================================================================
# SYSTEM STATUS
# ============================================================================

def render_system_status() -> None:
    """
    Render system status indicators.
    """
    st.subheader("System Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        api_ready = bool(st.secrets.get("GOOGLE_API_KEY", None))
        status = "✅ Ready" if api_ready else "⚠️ Not Configured"
        st.info(f"**API Connection**: {status}")

    with col2:
        db_ready = (VECTOR_DB_DIR / "collections").exists()
        status = "✅ Available" if db_ready else "⏳ Initializing"
        st.info(f"**Vector Database**: {status}")

    with col3:
        user_data_ready = USER_DATA_DIR.exists()
        status = "✅ Ready" if user_data_ready else "⚠️ Not Found"
        st.info(f"**User Data**: {status}")


# ============================================================================
# AFFIRMATION OF THE DAY
# ============================================================================

def render_daily_affirmation() -> None:
    """
    Render daily affirmation carousel.
    """
    affirmations = [
        "✨ You are stronger than you know.",
        "💚 Your feelings are valid.",
        "🌱 Growth happens one day at a time.",
        "🎯 You are worthy of care and compassion.",
        "🌟 Small steps lead to big changes.",
        "💪 You deserve happiness and peace.",
        "🌈 Your journey matters.",
        "🕊️ You are not alone in this.",
        "💝 Be kind to yourself today.",
        "🌸 You are enough, just as you are.",
    ]

    import random
    random.seed(hash(datetime.now().date()))
    daily_affirmation = random.choice(affirmations)

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {PRIMARY_GREEN} 0%, {ACCENT_GREEN} 100%);
        color: white;
        padding: 25px;
        border-radius: 10px;
        text-align: center;
        margin-top: 30px;
        font-size: 1.2em;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(107, 144, 128, 0.25);
    ">
        <strong>{daily_affirmation}</strong>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# PAGE RENDERING
# ============================================================================

def render_home_page() -> None:
    """
    Main home page renderer.
    """
    # Apply custom CSS
    inject_custom_css()

    # Check authentication
    if not st.session_state.get("logged_in", False):
        st.error("Please log in first.")
        st.stop()

    user_id = st.session_state.get("username", "User")

    # Render page content
    render_greeting_card(user_id)

    # Get metrics
    metrics = get_user_metrics(user_id)
    render_metrics_panel(metrics)

    # Render quick launch dock
    render_quick_launch_dock()

    # Render system status
    st.markdown("---")
    render_system_status()

    # Render daily affirmation
    render_daily_affirmation()

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #A8DADC; font-size: 0.9em;'>"
        "🌿 <strong>Therapeutic Companion</strong> | Built with care for your mental wellness 🌿"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    render_home_page()
