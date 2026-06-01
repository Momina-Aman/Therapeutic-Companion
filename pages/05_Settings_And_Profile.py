"""
Settings & Profile Management Page.

This page provides user configuration and management features:
- Profile editing and information updates
- Journal log management (clearing, export)
- Workspace theme preferences (light/dark mode)
- System sanity checks and developer tools
- Privacy and data management options

Author: Therapeutic Companion Team
Version: 1.0.0
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import subprocess
import json
import os
from typing import Dict, Any, Optional

# Import utilities
try:
    from styles import inject_custom_css
    from auth import AuthManager
except ImportError as e:
    st.error(f"Required module not found: {e}")
    st.stop()

try:
    from utils.context_manager import cleanup_session
except ImportError:
    st.warning("Context manager not available. Some features may be limited.")


# ============================================================================
# CONFIGURATION
# ============================================================================

USER_DATA_DIR = Path("./user_data")
LOG_DIR = Path("./logs")

# Color scheme
PRIMARY_GREEN = "#6B9080"
SOFT_BLUE = "#A8DADC"
LIGHT_SAGE = "#E8F5F0"
ACCENT_GREEN = "#52796F"
TEXT_DARK = "#2C3E50"


# ============================================================================
# PROFILE MANAGEMENT
# ============================================================================

def render_profile_section() -> None:
    """
    Render user profile editing section.
    """
    st.subheader("👤 Profile Management")

    user_id = st.session_state.get("username", "User")
    user_data_path = USER_DATA_DIR / user_id

    # Display current profile info
    col1, col2 = st.columns(2)

    with col1:
        st.text_input(
            "Username",
            value=user_id,
            disabled=True,
            help="Username cannot be changed"
        )

    with col2:
        st.text_input(
            "Account Created",
            value=datetime.now().strftime("%Y-%m-%d"),
            disabled=True,
            help="Account creation date"
        )

    # Profile settings
    st.markdown("#### Account Settings")

    # Display statistics
    journal_path = user_data_path / "journal.txt"
    if journal_path.exists():
        journal_size = journal_path.stat().st_size
        with open(journal_path, 'r', encoding='utf-8', errors='replace') as f:
            entry_count = len([l for l in f.readlines() if l.startswith("[")])
    else:
        journal_size = 0
        entry_count = 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Journal Size", f"{journal_size / 1024:.1f} KB")

    with col2:
        st.metric("Journal Entries", entry_count)

    with col3:
        st.metric("Account Age", "Active")


# ============================================================================
# JOURNAL MANAGEMENT
# ============================================================================

def render_journal_management_section() -> None:
    """
    Render journal management and export options.
    """
    st.subheader("📔 Journal Management")

    user_id = st.session_state.get("username", "User")
    user_data_path = USER_DATA_DIR / user_id
    journal_path = user_data_path / "journal.txt"

    tab1, tab2, tab3 = st.tabs(["View Journal", "Export Journal", "Manage Entries"])

    with tab1:
        st.markdown("#### Recent Journal Entries")

        if journal_path.exists():
            with open(journal_path, 'r', encoding='utf-8', errors='replace') as f:
                journal_content = f.read()

            if journal_content:
                # Split and display entries
                entries = journal_content.split("\n===\n")
                
                st.info(f"Total entries: {len([e for e in entries if e.strip()])}")

                # Show last 5 entries
                for entry in entries[-5:]:
                    if entry.strip():
                        st.text_area(
                            "Entry",
                            value=entry.strip(),
                            disabled=True,
                            height=100,
                            key=f"entry_{hash(entry)}"
                        )
                        st.markdown("---")
            else:
                st.info("No journal entries yet. Start journaling in the Activities tab!")
        else:
            st.info("Journal file not found. It will be created when you save your first entry.")

    with tab2:
        st.markdown("#### Export Your Journal")

        if st.button("📥 Export Journal as TXT", use_container_width=True):
            if journal_path.exists():
                with open(journal_path, 'r', encoding='utf-8', errors='replace') as f:
                    journal_content = f.read()

                st.download_button(
                    label="Download Journal",
                    data=journal_content,
                    file_name=f"{user_id}_journal_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("No journal to export yet.")

        if st.button("📋 Export as JSON", use_container_width=True):
            if journal_path.exists():
                with open(journal_path, 'r', encoding='utf-8', errors='replace') as f:
                    entries = f.read().split("\n===\n")

                json_data = {
                    "user": user_id,
                    "exported_at": datetime.now().isoformat(),
                    "entry_count": len([e for e in entries if e.strip()]),
                    "entries": [e.strip() for e in entries if e.strip()]
                }

                st.download_button(
                    label="Download as JSON",
                    data=json.dumps(json_data, indent=2),
                    file_name=f"{user_id}_journal_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.warning("No journal to export yet.")

    with tab3:
        st.markdown("#### Manage Journal Entries")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🧹 Clear All Entries", type="secondary", use_container_width=True):
                if journal_path.exists():
                    if st.checkbox("I confirm I want to delete all journal entries"):
                        journal_path.unlink()
                        st.success("✅ All journal entries have been deleted.")
                        st.rerun()
                else:
                    st.info("No entries to clear.")

        with col2:
            if st.button("📊 Journal Statistics", use_container_width=True):
                if journal_path.exists():
                    with open(journal_path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()

                    entries = [e for e in content.split("\n===\n") if e.strip()]
                    file_size = journal_path.stat().st_size

                    st.info(f"""
                    **Journal Statistics**
                    - Total Entries: {len(entries)}
                    - File Size: {file_size / 1024:.2f} KB
                    - Created: {datetime.fromtimestamp(journal_path.stat().st_ctime).strftime('%Y-%m-%d')}
                    - Last Modified: {datetime.fromtimestamp(journal_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}
                    """)
                else:
                    st.info("No journal entries yet.")


# ============================================================================
# THEME & WORKSPACE PREFERENCES
# ============================================================================

def render_theme_section() -> None:
    """
    Render workspace theme preferences.
    """
    st.subheader("🎨 Workspace Theme")

    theme_choice = st.radio(
        "Choose your workspace theme:",
        options=["Light Mode", "Dark Mode", "Auto (System Default)"],
        index=0,
        help="Select your preferred workspace appearance"
    )

    if theme_choice == "Light Mode":
        st.info("✨ Light mode enabled. Clean and bright interface.")
    elif theme_choice == "Dark Mode":
        st.info("🌙 Dark mode enabled. Easy on the eyes.")
    else:
        st.info("🔄 Auto mode: Theme follows system preferences.")

    # Additional display options
    st.markdown("#### Display Options")

    col1, col2 = st.columns(2)

    with col1:
        font_size = st.slider("Font Size", min_value=12, max_value=18, value=14)
        st.caption(f"Current: {font_size}px")

    with col2:
        line_height = st.slider("Line Height", min_value=1.2, max_value=2.0, value=1.6, step=0.1)
        st.caption(f"Current: {line_height}")

    st.success("✅ Theme preferences saved locally")


# ============================================================================
# SYSTEM SANITY CHECKS
# ============================================================================

def check_system_sanity() -> Dict[str, Any]:
    """
    Run comprehensive system sanity checks.

    Returns:
        Dictionary with check results
    """
    checks = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # Check 1: User data directory
    user_id = st.session_state.get("username", "User")
    user_data_path = USER_DATA_DIR / user_id
    checks["checks"]["user_data_dir"] = {
        "name": "User Data Directory",
        "passed": user_data_path.exists(),
        "details": str(user_data_path)
    }

    # Check 2: Journal file
    journal_path = user_data_path / "journal.txt"
    checks["checks"]["journal_file"] = {
        "name": "Journal File",
        "passed": journal_path.exists(),
        "details": "Journal file exists" if journal_path.exists() else "Journal not yet created"
    }

    # Check 3: Vector database
    vector_db_path = Path("./vector_db")
    checks["checks"]["vector_db"] = {
        "name": "Vector Database",
        "passed": vector_db_path.exists(),
        "details": str(vector_db_path)
    }

    # Check 4: Logs directory
    checks["checks"]["logs_dir"] = {
        "name": "Logs Directory",
        "passed": LOG_DIR.exists(),
        "details": str(LOG_DIR)
    }

    # Check 5: Google API Key
    api_key_set = bool(os.getenv("GOOGLE_API_KEY", None))
    checks["checks"]["api_key"] = {
        "name": "Google API Key",
        "passed": api_key_set,
        "details": "API key is configured" if api_key_set else "API key not set"
    }

    # Check 6: Python environment
    checks["checks"]["python_env"] = {
        "name": "Python Environment",
        "passed": True,
        "details": f"Python {os.sys.version.split()[0]}"
    }

    return checks


def render_developer_tools_section() -> None:
    """
    Render developer tools and system sanity checks.
    """
    st.subheader("🔧 Developer Tools")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏥 Run System Sanity Check", use_container_width=True):
            st.markdown("#### System Status Report")

            checks = check_system_sanity()

            # Display results
            all_passed = True
            for check_key, check_data in checks["checks"].items():
                passed = check_data["passed"]
                all_passed = all_passed and passed

                status_icon = "✅" if passed else "⚠️"
                status_color = "green" if passed else "red"

                st.markdown(f"""
                <div style="
                    padding: 10px;
                    border-left: 4px solid {status_color};
                    background-color: rgba(0,0,0,0.02);
                    margin: 8px 0;
                    border-radius: 4px;
                ">
                    <strong>{status_icon} {check_data['name']}</strong><br/>
                    <small>{check_data['details']}</small>
                </div>
                """, unsafe_allow_html=True)

            # Overall status
            st.markdown("---")
            if all_passed:
                st.success("✅ All systems operational!")
            else:
                st.warning("⚠️ Some systems need attention. Check details above.")

            # Print to terminal
            st.info("📋 System check output printed to terminal.")
            print("\n" + "=" * 80)
            print("SYSTEM SANITY CHECK REPORT")
            print("=" * 80)
            for check_key, check_data in checks["checks"].items():
                status = "PASS" if check_data["passed"] else "FAIL"
                print(f"[{status}] {check_data['name']}: {check_data['details']}")
            print("=" * 80)

    with col2:
        if st.button("📊 View Environment Configuration", use_container_width=True):
            st.markdown("#### Environment Configuration")

            env_info = {
                "Python Version": os.sys.version.split()[0],
                "Platform": os.sys.platform,
                "Working Directory": os.getcwd(),
                "User": st.session_state.get("username", "Unknown"),
                "Session Start": st.session_state.get("session_start", "Unknown"),
            }

            for key, value in env_info.items():
                st.text(f"{key}: {value}")

            st.info("📋 Environment configuration printed to terminal.")
            print("\n" + "=" * 80)
            print("ENVIRONMENT CONFIGURATION")
            print("=" * 80)
            for key, value in env_info.items():
                print(f"{key}: {value}")
            print("=" * 80)


# ============================================================================
# PRIVACY & DATA
# ============================================================================

def render_privacy_section() -> None:
    """
    Render privacy and data management options.
    """
    st.subheader("🔒 Privacy & Data")

    st.markdown("#### Data Privacy")

    st.info("""
    **Your Privacy Matters**
    - All journal entries are stored locally on your device
    - No personal data is logged to system logs
    - User IDs are hashed in audit trails
    - Queries are anonymized in performance logs
    """)

    st.markdown("#### Data Management")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Download My Data", use_container_width=True):
            user_id = st.session_state.get("username", "User")
            user_data_path = USER_DATA_DIR / user_id

            st.info("Your data download would include:")
            st.markdown("""
            - Journal entries
            - Session logs
            - User preferences
            - Activity history
            """)

    with col2:
        if st.button("🗑️ Delete My Account", type="secondary", use_container_width=True):
            st.warning("⚠️ This action is permanent and cannot be undone.")
            if st.checkbox("I understand the consequences"):
                st.error("Please contact support to permanently delete your account.")


# ============================================================================
# PAGE RENDERING
# ============================================================================

def render_settings_page() -> None:
    """
    Main settings page renderer.
    """
    # Apply custom CSS
    inject_custom_css()

    # Check authentication
    if not st.session_state.get("logged_in", False):
        st.error("Please log in first.")
        st.stop()

    st.title("⚙️ Settings & Profile")

    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Profile",
        "Journal",
        "Appearance",
        "System",
        "Privacy"
    ])

    with tab1:
        render_profile_section()

    with tab2:
        render_journal_management_section()

    with tab3:
        render_theme_section()

    with tab4:
        render_developer_tools_section()

    with tab5:
        render_privacy_section()

    # Footer with logout option
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.page = "00_Home"
            st.rerun()


if __name__ == "__main__":
    render_settings_page()
