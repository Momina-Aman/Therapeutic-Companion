"""
Admin Dashboard - System Monitoring & Performance Metrics.

Hidden admin page displaying:
- Real-time system health metrics
- Performance analytics (latency charts, throughput)
- Vector database statistics
- User system overview
- Manual data re-indexing trigger
- Error logs and alerts

Access: Password-protected (default: "admin" for demo)
Route: http://localhost:8501/?page=03_Clinic_Finder (must add 04_Admin_Dashboard.py to pages/)

Usage:
    - Navigate to Admin Dashboard in Streamlit menu (if authenticated)
    - Enter admin password
    - View metrics and trigger data refresh as needed

Security: Password validation, session state verification, audit logging
"""

import streamlit as st
from auth import check_auth
from pathlib import Path
import json
from datetime import datetime, timedelta
import subprocess
import hashlib

try:
    from logger_utils import (
        get_logger, hash_user_id, get_latency_stats, get_error_summary
    )
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


# ============================================================================
# CONFIGURATION
# ============================================================================

# Admin password (hash for production: hash.sha256(b"admin").hexdigest())
ADMIN_PASSWORD_HASH = hashlib.sha256(b"admin").hexdigest()
LOG_DIR = Path("./logs")
USER_DATA_DIR = Path("./user_data")
VECTOR_DB_PATH = Path("./vector_db")


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Admin Dashboard - Therapeutic Companion",
    page_icon="⚙️",
    layout="wide"
)

# Check authentication
if not check_auth(st.session_state):
    st.error("Please log in to access this page.")
    st.stop()


# ============================================================================
# ADMIN PASSWORD VERIFICATION
# ============================================================================

def verify_admin_password(password: str) -> bool:
    """Verify admin password hash."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == ADMIN_PASSWORD_HASH


def check_admin_access():
    """Check if user has admin access."""
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    return st.session_state.admin_authenticated


# ============================================================================
# ADMIN ACCESS GATE
# ============================================================================

if not check_admin_access():
    st.warning("🔒 Admin Dashboard - Access Required")

    col1, col2 = st.columns([2, 1])

    with col1:
        password = st.text_input(
            "Enter admin password:",
            type="password",
            key="admin_password"
        )

    with col2:
        if st.button("Authenticate", use_container_width=True):
            if password and verify_admin_password(password):
                st.session_state.admin_authenticated = True
                st.success("✅ Admin access granted")
                st.rerun()
            elif password:
                st.error("❌ Invalid password")

    st.info("Only administrators can access performance metrics and system controls.")
    st.stop()


# ============================================================================
# LOGGER SETUP
# ============================================================================

if LOGGER_AVAILABLE:
    admin_logger = get_logger("admin_dashboard")
    admin_logger.info(
        "Admin dashboard accessed",
        extra={"user_hash": hash_user_id(st.session_state.username)}
    )


# ============================================================================
# SYSTEM METRICS FUNCTIONS
# ============================================================================

def get_database_stats() -> dict:
    """Get SQLite database statistics."""
    try:
        import sqlite3

        db_path = Path("./therapeutic_companion.db")

        if not db_path.exists():
            return {"status": "not_found", "message": "Database file not found"}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get users count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        # Get database file size
        db_size_mb = db_path.stat().st_size / (1024 * 1024)

        conn.close()

        return {
            "status": "ok",
            "user_count": user_count,
            "file_size_mb": round(db_size_mb, 2),
            "last_modified": datetime.fromtimestamp(db_path.stat().st_mtime).isoformat()
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_vector_db_stats() -> dict:
    """Get ChromaDB vector store statistics."""
    if not CHROMADB_AVAILABLE:
        return {"status": "unavailable", "message": "ChromaDB not installed"}

    try:
        if not VECTOR_DB_PATH.exists():
            return {"status": "not_found", "message": "Vector store not initialized"}

        # Get vector db directory size
        total_size = 0
        for file in VECTOR_DB_PATH.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size

        db_size_mb = total_size / (1024 * 1024)

        # Try to connect and get collection stats
        try:
            client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
            collections = client.list_collections()
            collection_count = len(collections)

            doc_count = 0
            for collection in collections:
                if hasattr(collection, '_client'):
                    # Count documents in collection
                    try:
                        results = collection.get(limit=1)
                        doc_count += collection.count()
                    except:
                        pass

        except Exception as e:
            collection_count = 0
            doc_count = 0

        return {
            "status": "ok",
            "directory_size_mb": round(db_size_mb, 2),
            "collections": collection_count,
            "estimated_documents": doc_count if doc_count > 0 else "unknown",
            "last_modified": datetime.fromtimestamp(VECTOR_DB_PATH.stat().st_mtime).isoformat()
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_user_data_stats() -> dict:
    """Get user data directory statistics."""
    try:
        if not USER_DATA_DIR.exists():
            return {
                "status": "not_found",
                "message": "User data directory not found",
                "total_size_mb": 0,
                "journal_files": 0,
                "user_directories": 0
            }

        total_size = 0
        journal_count = 0
        user_count = 0

        for user_dir in USER_DATA_DIR.iterdir():
            if user_dir.is_dir():
                user_count += 1

                for file in user_dir.iterdir():
                    if file.is_file():
                        total_size += file.stat().st_size

                        if file.name == "journal.txt":
                            journal_count += 1

        return {
            "status": "ok",
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "user_directories": user_count,
            "journal_files": journal_count
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_system_health() -> dict:
    """Aggregate system health metrics."""
    db_stats = get_database_stats()
    vector_stats = get_vector_db_stats()
    user_stats = get_user_data_stats()

    latency_stats = {}
    if LOGGER_AVAILABLE:
        latency_stats = get_latency_stats(hours=24)

    return {
        "timestamp": datetime.now().isoformat(),
        "database": db_stats,
        "vector_store": vector_stats,
        "user_data": user_stats,
        "performance": latency_stats
    }


# ============================================================================
# ADMIN DASHBOARD SECTIONS
# ============================================================================

def render_metrics_overview():
    """Render key metrics overview."""
    st.subheader("📊 System Metrics Overview")

    health = get_system_health()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        db_stats = health["database"]
        user_count = db_stats.get("user_count", 0)
        st.metric(
            "Registered Users",
            user_count,
            delta="Active accounts"
        )

    with col2:
        vector_stats = health["vector_store"]
        doc_count = vector_stats.get("estimated_documents", 0)
        st.metric(
            "Vector Store Docs",
            doc_count,
            delta="Indexed documents"
        )

    with col3:
        user_stats = health["user_data"]
        journal_count = user_stats.get("journal_files", 0)
        st.metric(
            "Journal Entries",
            journal_count,
            delta="Saved journals"
        )

    with col4:
        perf = health["performance"]
        if "avg_ms" in perf:
            avg_latency = perf["avg_ms"]
            st.metric(
                "Avg Latency",
                f"{avg_latency:.0f}ms",
                delta="Last 24h"
            )
        else:
            st.metric("Avg Latency", "N/A", delta="No data yet")

    st.markdown("---")


def render_detailed_stats():
    """Render detailed statistics."""
    st.subheader("📈 Detailed Statistics")

    health = get_system_health()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Database**")
        db_stats = health["database"]

        if db_stats["status"] == "ok":
            st.write(f"• Users: {db_stats['user_count']}")
            st.write(f"• Size: {db_stats['file_size_mb']} MB")
            st.write(f"• Last Modified: {db_stats.get('last_modified', 'N/A')}")
        else:
            st.warning(f"Status: {db_stats.get('message', 'Unknown')}")

        st.write("\n**User Data**")
        user_stats = health["user_data"]

        if user_stats["status"] == "ok":
            st.write(f"• Users: {user_stats['user_directories']}")
            st.write(f"• Journals: {user_stats['journal_files']}")
            st.write(f"• Total Size: {user_stats['total_size_mb']} MB")
        else:
            st.warning(f"Status: {user_stats.get('message', 'Unknown')}")

    with col2:
        st.write("**Vector Store**")
        vector_stats = health["vector_store"]

        if vector_stats["status"] == "ok":
            st.write(f"• Size: {vector_stats['directory_size_mb']} MB")
            st.write(f"• Collections: {vector_stats['collections']}")
            st.write(f"• Documents: {vector_stats['estimated_documents']}")
            st.write(f"• Last Modified: {vector_stats.get('last_modified', 'N/A')}")
        else:
            st.warning(f"Status: {vector_stats.get('message', 'Unknown')}")

        st.write("\n**Performance (24h)**")
        perf = health["performance"]

        if perf and "count" in perf:
            st.write(f"• Samples: {perf['count']}")
            st.write(f"• Min: {perf['min_ms']:.0f}ms")
            st.write(f"• Max: {perf['max_ms']:.0f}ms")
            st.write(f"• Avg: {perf['avg_ms']:.0f}ms")
            st.write(f"• P95: {perf['p95_ms']:.0f}ms")
        else:
            st.info("No performance data yet")


def render_latency_chart():
    """Render latency performance chart."""
    st.subheader("⚡ Response Latency Trend")

    if not LOGGER_AVAILABLE:
        st.info("Logger utilities not available")
        return

    try:
        latency_log = LOG_DIR / "latency.log"

        if not latency_log.exists():
            st.info("No latency data collected yet")
            return

        # Parse log entries
        entries = []
        with open(latency_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if not entries:
            st.info("No latency entries found")
            return

        # Extract latencies and timestamps
        latencies = []
        timestamps = []

        for entry in entries[-100:]:  # Last 100 entries
            if "total_latency_ms" in entry:
                latencies.append(entry["total_latency_ms"])
                try:
                    ts = datetime.fromisoformat(entry["timestamp"])
                    timestamps.append(ts)
                except:
                    timestamps.append(datetime.now())

        if latencies:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(range(len(latencies)), latencies, marker='o', linestyle='-', color='#6B9080')
            ax.set_xlabel('Request #')
            ax.set_ylabel('Latency (ms)')
            ax.set_title('Response Latency Over Time')
            ax.grid(True, alpha=0.3)

            st.pyplot(fig)

            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Min Latency", f"{min(latencies):.0f}ms")
            with col2:
                st.metric("Avg Latency", f"{sum(latencies)/len(latencies):.0f}ms")
            with col3:
                st.metric("Max Latency", f"{max(latencies):.0f}ms")
        else:
            st.info("No latency measurements available")

    except Exception as e:
        st.error(f"Error rendering chart: {e}")


def render_error_summary():
    """Render error summary."""
    st.subheader("⚠️ Error Summary")

    if not LOGGER_AVAILABLE:
        st.info("Logger utilities not available")
        return

    try:
        error_summary = get_error_summary()

        if error_summary:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write("**Error Types (24h)**")
                for error_type, count in list(error_summary.items())[:10]:
                    st.write(f"• {error_type}: {count}")

            with col2:
                st.metric("Total Error Types", len(error_summary))
                total_errors = sum(error_summary.values())
                st.metric("Total Errors", total_errors)
        else:
            st.success("✅ No errors recorded")

    except Exception as e:
        st.error(f"Error loading error summary: {e}")


def render_control_panel():
    """Render admin control panel."""
    st.subheader("🎛️ Admin Controls")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Data Management**")

        if st.button(
            "🔄 Re-index Vector Store (ingest.py)",
            use_container_width=True,
            help="Reload data from ./dataa/ and refresh ChromaDB"
        ):
            try:
                with st.spinner("Re-indexing vector store..."):
                    result = subprocess.run(
                        ["python", "ingest.py", "--reingest"],
                        cwd=Path.cwd(),
                        capture_output=True,
                        timeout=300
                    )

                    if result.returncode == 0:
                        st.success("✅ Vector store re-indexed successfully")

                        if LOGGER_AVAILABLE:
                            admin_logger.info(
                                "Vector store re-indexed by admin",
                                extra={
                                    "user_hash": hash_user_id(st.session_state.username),
                                    "status": "success"
                                }
                            )
                    else:
                        error_msg = result.stderr.decode() if result.stderr else "Unknown error"
                        st.error(f"Re-indexing failed: {error_msg}")

                        if LOGGER_AVAILABLE:
                            admin_logger.error(
                                "Vector store re-index failed",
                                extra={"error": error_msg}
                            )

            except subprocess.TimeoutExpired:
                st.error("Re-indexing timed out (> 5 minutes)")
            except Exception as e:
                st.error(f"Error running ingest.py: {e}")

        st.write("\n**Logs**")

        if st.button("📥 Download Logs", use_container_width=True):
            # Create zip of logs
            import zipfile
            import io

            zip_buffer = io.BytesIO()

            try:
                with zipfile.ZipFile(zip_buffer, 'w') as zf:
                    for log_file in LOG_DIR.glob("*.log"):
                        zf.write(log_file, arcname=log_file.name)

                zip_buffer.seek(0)
                st.download_button(
                    label="Download Logs ZIP",
                    data=zip_buffer.getvalue(),
                    file_name=f"logs_{datetime.now().isoformat()}.zip",
                    mime="application/zip"
                )
            except Exception as e:
                st.error(f"Error creating log archive: {e}")

    with col2:
        st.write("**System Actions**")

        if st.button("🧹 Clear Cache", use_container_width=True):
            try:
                import gc

                gc.collect()
                st.success("✅ Cache cleared")

                if LOGGER_AVAILABLE:
                    admin_logger.info("Cache cleared by admin")

            except Exception as e:
                st.error(f"Error clearing cache: {e}")

        st.write("\n**Health Check**")

        if st.button("🏥 Run Health Check", use_container_width=True):
            with st.spinner("Checking system health..."):
                health = get_system_health()

                col1, col2 = st.columns(2)

                checks = {
                    "Database": health["database"]["status"],
                    "Vector Store": health["vector_store"]["status"],
                    "User Data": health["user_data"]["status"]
                }

                for check_name, status in checks.items():
                    if status == "ok":
                        st.success(f"✅ {check_name}: OK")
                    elif status == "not_found":
                        st.warning(f"⚠️ {check_name}: Not found (will be created on first use)")
                    else:
                        st.error(f"❌ {check_name}: {status}")


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    """Render admin dashboard."""
    st.title("⚙️ Admin Dashboard")

    st.write("System monitoring, performance analytics, and administrative controls.")

    st.markdown("---")

    render_metrics_overview()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Detailed Stats",
        "⚡ Latency",
        "⚠️ Errors",
        "🎛️ Controls"
    ])

    with tab1:
        render_detailed_stats()

    with tab2:
        render_latency_chart()

    with tab3:
        render_error_summary()

    with tab4:
        render_control_panel()

    st.markdown("---")

    st.info(
        "📌 **Last Updated**: " +
        datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
        " | **Admin User**: " +
        st.session_state.username
    )


if __name__ == "__main__":
    main()
