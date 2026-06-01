"""
Utils Package - Therapeutic Companion Utilities.

This package contains utility modules for session management, context
consolidation, and cross-module integration.

Modules:
    - context_manager: Session state and user isolation management
"""

__version__ = "1.0.0"
__author__ = "Therapeutic Companion Team"

# Make utilities available at package level
try:
    from utils.context_manager import (
        ContextManager,
        get_context_manager,
        cleanup_session,
        initialize_session_state,
        get_user_telemetry,
    )

    __all__ = [
        "ContextManager",
        "get_context_manager",
        "cleanup_session",
        "initialize_session_state",
        "get_user_telemetry",
    ]

except ImportError as e:
    print(f"Warning: Could not import utils submodules: {e}")
    __all__ = []
