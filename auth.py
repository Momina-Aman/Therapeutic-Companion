"""
Authentication module for Therapeutic Companion.

This module provides robust user authentication using Bcrypt hashing and SQLite.
It includes functions for user registration, login, and credential verification.
"""

import sqlite3
import bcrypt
import os
from pathlib import Path
from datetime import datetime


class AuthManager:
    """Manages user authentication, registration, and database operations."""

    def __init__(self, db_path: str = "therapeutic_companion.db"):
        """
        Initialize the AuthManager with database path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self) -> None:
        """
        Initialize the SQLite database with users table if it doesn't exist.

        Raises:
            sqlite3.Error: If database connection or creation fails.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database initialization error: {e}") from e

    def hash_password(self, password: str) -> str:
        """
        Hash a plain-text password using Bcrypt.

        Args:
            password: The plain-text password to hash.

        Returns:
            The hashed password as a string.
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a hashed password.

        Args:
            password: The plain-text password to verify.
            hashed_password: The hashed password from the database.

        Returns:
            True if password matches, False otherwise.
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        Register a new user with username and password.

        Args:
            username: The desired username.
            password: The desired password.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate inputs
            if not username or not password:
                return False, "Username and password cannot be empty."

            if len(username) < 3:
                return False, "Username must be at least 3 characters long."

            if len(password) < 6:
                return False, "Password must be at least 6 characters long."

            # Hash password
            hashed_password = self.hash_password(password)

            # Insert into database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            # Create user-specific data directory
            user_dir = Path(f"./user_data/{username}")
            user_dir.mkdir(parents=True, exist_ok=True)

            return True, "Registration successful! Please log in."

        except sqlite3.IntegrityError:
            return False, "Username already exists. Please choose another."
        except sqlite3.Error as e:
            return False, f"Database error during registration: {e}"

    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user with username and password.

        Args:
            username: The username to authenticate.
            password: The password to verify.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, password FROM users WHERE username = ?",
                (username,)
            )

            result = cursor.fetchone()
            conn.close()

            if result is None:
                return False, "Username not found."

            user_id, hashed_password = result

            if self.verify_password(password, hashed_password):
                return True, "Login successful!"
            else:
                return False, "Incorrect password."

        except sqlite3.Error as e:
            return False, f"Database error during login: {e}"

    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database.

        Args:
            username: The username to check.

        Returns:
            True if user exists, False otherwise.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()

            return result is not None

        except sqlite3.Error as e:
            raise sqlite3.Error(f"Database error while checking user existence: {e}") from e


def check_auth(session_state) -> bool:
    """
    Check if the current user is authenticated.

    Args:
        session_state: The Streamlit session state object.

    Returns:
        True if user is logged in, False otherwise.
    """
    return session_state.get("logged_in", False) and session_state.get("username") is not None
