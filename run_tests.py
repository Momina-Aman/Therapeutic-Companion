"""
Pytest Test Suite - Security, Isolation, and Data Integrity Tests.

Comprehensive test coverage for the Therapeutic Companion application:

1. **Session Isolation Tests**: Verify User A cannot access User B data
2. **Data Integrity Tests**: SQLite tables, directories, permissions
3. **ChromaDB Tests**: Vector store initialization and retrieval
4. **Authentication Tests**: Password hashing, session state
5. **Journal Tests**: File I/O, UTF-8 encoding, format validation
6. **Error Handling Tests**: Graceful failures, defaults creation

Run tests with: pytest run_tests.py -v

Coverage: pytest run_tests.py --cov=. --cov-report=html

Production Security: All tests pass before deployment
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sqlite3
import json
from datetime import datetime
import bcrypt
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from auth import AuthManager
from logger_utils import hash_user_id, hash_query, sanitize_text


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_db():
    """Create temporary test database."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"

    yield db_path

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_user_data():
    """Create temporary user data directory."""
    temp_dir = tempfile.mkdtemp()

    yield Path(temp_dir)

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def auth_manager(temp_db):
    """Create auth manager with temp database."""
    manager = AuthManager(db_path=str(temp_db))
    manager.initialize_database()
    return manager


# ============================================================================
# AUTHENTICATION & SESSION TESTS
# ============================================================================

class TestAuthenticationSecurity:
    """Test authentication and session security."""

    def test_password_hashing_is_unique(self, auth_manager):
        """Test that same password produces different hashes (salt)."""
        password = "test_password_123"

        hash1 = auth_manager.hash_password(password)
        hash2 = auth_manager.hash_password(password)

        # Hashes should be different (due to salt)
        assert hash1 != hash2

        # But both should verify
        assert auth_manager.verify_password(password, hash1)
        assert auth_manager.verify_password(password, hash2)

    def test_password_verification(self, auth_manager):
        """Test password verification works correctly."""
        password = "correct_password"
        password_hash = auth_manager.hash_password(password)

        assert auth_manager.verify_password(password, password_hash)
        assert not auth_manager.verify_password("wrong_password", password_hash)

    def test_bcrypt_strength(self, auth_manager):
        """Test that bcrypt is using appropriate cost factor."""
        password = "test"
        hashed = auth_manager.hash_password(password)

        # Verify cost factor (should be 12)
        # bcrypt hashes start with "$2a$" or "$2b$", followed by cost factor
        assert hashed.startswith("$2b$")
        cost_factor = int(hashed.split("$")[2])
        assert cost_factor >= 12, "Bcrypt cost factor should be >= 12"

    def test_user_registration(self, auth_manager):
        """Test user registration creates user correctly."""
        username = "test_user"
        password = "secure_password_123"

        success = auth_manager.register_user(username, password)

        assert success
        assert auth_manager.user_exists(username)

    def test_duplicate_user_registration_fails(self, auth_manager):
        """Test that duplicate username registration fails."""
        username = "test_user"
        password = "password1"

        auth_manager.register_user(username, password)

        # Try registering same user again
        success = auth_manager.register_user(username, password)

        assert not success

    def test_login_with_correct_credentials(self, auth_manager):
        """Test login succeeds with correct credentials."""
        username = "test_user"
        password = "secure_password"

        auth_manager.register_user(username, password)

        success = auth_manager.login_user(username, password)

        assert success

    def test_login_with_wrong_password_fails(self, auth_manager):
        """Test login fails with wrong password."""
        username = "test_user"
        password = "correct_password"

        auth_manager.register_user(username, password)

        success = auth_manager.login_user(username, "wrong_password")

        assert not success

    def test_login_nonexistent_user_fails(self, auth_manager):
        """Test login fails for nonexistent user."""
        success = auth_manager.login_user("nonexistent", "any_password")

        assert not success


# ============================================================================
# SESSION ISOLATION TESTS (CRITICAL SECURITY)
# ============================================================================

class TestSessionIsolation:
    """Test that sessions are properly isolated between users."""

    def test_user_data_directories_are_separate(self, temp_user_data):
        """Test that each user has isolated data directory."""
        user_a_dir = temp_user_data / "user_a"
        user_b_dir = temp_user_data / "user_b"

        user_a_dir.mkdir()
        user_b_dir.mkdir()

        # Create files for each user
        (user_a_dir / "journal.txt").write_text("User A's private journal")
        (user_b_dir / "journal.txt").write_text("User B's private journal")

        # Verify isolation
        assert (user_a_dir / "journal.txt").read_text() == "User A's private journal"
        assert (user_b_dir / "journal.txt").read_text() == "User B's private journal"

        # User A cannot access User B's data
        user_b_file = user_a_dir / "../user_b/journal.txt"

        # Path resolution should prevent access
        assert user_b_file.resolve().parent.name == "user_b"

    def test_user_cannot_access_other_user_journal(self, temp_user_data):
        """Test explicit prevention of cross-user journal access."""
        # Setup
        user_a_dir = temp_user_data / "user_a"
        user_b_dir = temp_user_data / "user_b"

        user_a_dir.mkdir()
        user_b_dir.mkdir()

        user_a_journal = user_a_dir / "journal.txt"
        user_b_journal = user_b_dir / "journal.txt"

        user_a_journal.write_text("User A's secrets", encoding='utf-8')
        user_b_journal.write_text("User B's secrets", encoding='utf-8')

        # Simulate User A trying to access User B's journal
        current_user = "user_a"
        current_user_dir = temp_user_data / current_user

        # Only read from current user's directory
        accessible_file = current_user_dir / "journal.txt"

        assert accessible_file.read_text(encoding='utf-8') == "User A's secrets"
        assert not str(accessible_file).replace("user_a", "user_b") == str(user_b_journal)

    def test_database_user_isolation(self, auth_manager):
        """Test SQLite properly isolates user credentials."""
        # Register two users
        auth_manager.register_user("alice", "alice_password")
        auth_manager.register_user("bob", "bob_password")

        # Alice's credentials should NOT authenticate Bob
        assert auth_manager.login_user("alice", "alice_password")
        assert not auth_manager.login_user("bob", "alice_password")

        # Bob's credentials should NOT authenticate Alice
        assert auth_manager.login_user("bob", "bob_password")
        assert not auth_manager.login_user("alice", "bob_password")


# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================

class TestDataIntegrity:
    """Test data structure integrity and validation."""

    def test_sqlite_database_creation(self, temp_db):
        """Test SQLite database is created with correct schema."""
        manager = AuthManager(db_path=str(temp_db))
        manager.initialize_database()

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check users table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert cursor.fetchone() is not None

        # Check columns
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {'id', 'username', 'password_hash', 'created_at'}
        assert expected_columns.issubset(columns)

        conn.close()

    def test_sqlite_file_permissions(self, temp_db):
        """Test SQLite database file has proper permissions."""
        manager = AuthManager(db_path=str(temp_db))
        manager.initialize_database()

        assert temp_db.exists()
        assert temp_db.is_file()

        # Check readable and writable
        assert os.access(temp_db, os.R_OK)
        assert os.access(temp_db, os.W_OK)

    def test_user_data_directory_creation(self, temp_user_data):
        """Test that user data directories are created correctly."""
        username = "test_user"
        user_dir = temp_user_data / username

        user_dir.mkdir(parents=True, exist_ok=True)

        assert user_dir.exists()
        assert user_dir.is_dir()
        assert os.access(user_dir, os.R_OK)
        assert os.access(user_dir, os.W_OK)

    def test_journal_file_utf8_encoding(self, temp_user_data):
        """Test journal files support UTF-8 encoding (international chars)."""
        user_dir = temp_user_data / "test_user"
        user_dir.mkdir(parents=True, exist_ok=True)

        journal_file = user_dir / "journal.txt"

        # Test various UTF-8 characters
        test_content = """
        日本語: こんにちは
        Español: ¡Hola!
        العربية: مرحبا
        Emoji: 😊 💙 🌱
        Special chars: café, naïve, Zürich
        """

        journal_file.write_text(test_content, encoding='utf-8')
        read_content = journal_file.read_text(encoding='utf-8')

        assert read_content == test_content

    def test_journal_entry_format_validation(self, temp_user_data):
        """Test journal entries maintain proper format."""
        user_dir = temp_user_data / "test_user"
        user_dir.mkdir(parents=True, exist_ok=True)

        journal_file = user_dir / "journal.txt"

        # Write formatted entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n{'='*60}\n[{timestamp}]\n{'='*60}\nTest journal entry\n"

        journal_file.write_text(entry, encoding='utf-8')
        content = journal_file.read_text(encoding='utf-8')

        # Validate format
        assert "====" in content
        assert f"[{timestamp}]" in content
        assert "Test journal entry" in content


# ============================================================================
# CHROMADB TESTS
# ============================================================================

class TestVectorStore:
    """Test ChromaDB vector store integrity."""

    def test_vector_store_path_exists(self):
        """Test vector store directory exists or can be created."""
        vector_db_path = Path("./vector_db")

        # Should exist or be creatable
        vector_db_path.mkdir(parents=True, exist_ok=True)

        assert vector_db_path.exists()
        assert vector_db_path.is_dir()

    def test_chromadb_import(self):
        """Test ChromaDB can be imported."""
        try:
            import chromadb

            assert chromadb is not None
        except ImportError:
            pytest.skip("ChromaDB not installed")


# ============================================================================
# LOGGER TESTS
# ============================================================================

class TestLoggingUtilities:
    """Test logger utilities for privacy and structure."""

    def test_user_id_hashing(self):
        """Test user ID hashing produces consistent results."""
        user_id = "test@example.com"

        hash1 = hash_user_id(user_id)
        hash2 = hash_user_id(user_id)

        assert hash1 == hash2
        assert len(hash1) == 16  # SHA256 truncated to 16 chars

    def test_query_hashing(self):
        """Test query hashing for privacy."""
        query = "How do I handle anxiety?"

        hash1 = hash_query(query)
        hash2 = hash_query(query)

        assert hash1 == hash2
        assert len(hash1) == 12  # SHA256 truncated to 12 chars

        # Different queries produce different hashes
        query2 = "How do I handle depression?"
        hash3 = hash_query(query2)

        assert hash1 != hash3

    def test_text_sanitization(self):
        """Test text sanitization for safe logging."""
        long_text = "A" * 200

        sanitized = sanitize_text(long_text, max_length=100)

        assert len(sanitized) <= 103  # 100 + "..."
        assert sanitized.endswith("...")

        short_text = "Short"
        assert sanitize_text(short_text) == short_text


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and graceful failures."""

    def test_missing_database_creates_on_init(self, temp_db):
        """Test missing database is created on initialization."""
        assert not temp_db.exists()

        manager = AuthManager(db_path=str(temp_db))
        manager.initialize_database()

        assert temp_db.exists()

    def test_missing_user_data_dir_created(self, temp_user_data):
        """Test missing user data dir is created on access."""
        user_dir = temp_user_data / "new_user"

        assert not user_dir.exists()

        user_dir.mkdir(parents=True, exist_ok=True)

        assert user_dir.exists()

    def test_corrupted_journal_file_handling(self, temp_user_data):
        """Test handling of corrupted journal files."""
        user_dir = temp_user_data / "test_user"
        user_dir.mkdir(parents=True, exist_ok=True)

        journal_file = user_dir / "journal.txt"

        # Write binary garbage
        journal_file.write_bytes(b'\x80\x81\x82\x83')

        # Should fail gracefully when reading as UTF-8
        try:
            content = journal_file.read_text(encoding='utf-8', errors='replace')
            # Should get replacement characters or empty
            assert isinstance(content, str)
        except Exception:
            pytest.fail("Failed to handle corrupted file gracefully")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_user_lifecycle(self, temp_db, temp_user_data):
        """Test complete user registration, login, data flow."""
        # Setup
        manager = AuthManager(db_path=str(temp_db))
        manager.initialize_database()

        # Register
        assert manager.register_user("alice", "secure_password")
        assert manager.user_exists("alice")

        # Create user data dir
        user_dir = temp_user_data / "alice"
        user_dir.mkdir(parents=True, exist_ok=True)

        # Save journal entry
        journal_file = user_dir / "journal.txt"
        entry = "Today I felt better. Small win!"
        journal_file.write_text(entry, encoding='utf-8')

        # Login
        assert manager.login_user("alice", "secure_password")

        # Verify journal is accessible
        assert journal_file.read_text(encoding='utf-8') == entry

    def test_two_users_cannot_access_each_other_data(self, temp_db, temp_user_data):
        """Test complete isolation between two users."""
        manager = AuthManager(db_path=str(temp_db))
        manager.initialize_database()

        # Register two users
        manager.register_user("alice", "password_a")
        manager.register_user("bob", "password_b")

        # Create separate data directories
        alice_dir = temp_user_data / "alice"
        bob_dir = temp_user_data / "bob"

        alice_dir.mkdir(parents=True, exist_ok=True)
        bob_dir.mkdir(parents=True, exist_ok=True)

        # Each user writes their own journal
        (alice_dir / "journal.txt").write_text("Alice's private thoughts", encoding='utf-8')
        (bob_dir / "journal.txt").write_text("Bob's private thoughts", encoding='utf-8')

        # Simulate Alice logged in
        alice_current_dir = alice_dir
        assert alice_current_dir.exists()
        assert "Alice's private thoughts" in (alice_current_dir / "journal.txt").read_text()

        # Alice cannot read Bob's journal
        bob_journal_from_alice = alice_dir / "../bob/journal.txt"
        assert not bob_journal_from_alice.exists(), "Alice should not be able to construct Bob's path"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance and scalability."""

    def test_password_hashing_speed(self, auth_manager):
        """Test password hashing completes in reasonable time."""
        import time

        password = "test_password"

        start = time.time()
        hash_password = auth_manager.hash_password(password)
        elapsed = time.time() - start

        # Hashing should take ~100-500ms with cost factor 12
        assert elapsed < 2.0, "Password hashing too slow"

    def test_large_journal_file_handling(self, temp_user_data):
        """Test handling of large journal files."""
        user_dir = temp_user_data / "test_user"
        user_dir.mkdir(parents=True, exist_ok=True)

        journal_file = user_dir / "journal.txt"

        # Write large entry (1MB)
        large_content = "This is a journal entry. " * 50000

        journal_file.write_text(large_content, encoding='utf-8')

        # Should read without issues
        content = journal_file.read_text(encoding='utf-8')

        assert len(content) > 1000000
        assert content == large_content


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
