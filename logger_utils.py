"""
Logger Utilities - Structured Logging Without PII.

This module implements production-grade structured logging that captures:
- System performance metrics (latency, throughput)
- RAG retrieval performance (token counts, doc counts)
- User interaction metrics (aggregated, non-PII)
- API usage and rate limiting events
- Security and audit events

Privacy-First Design:
- Never logs raw conversation text
- Never logs usernames (only anonymized user_ids)
- Never logs personal health information
- Logs only aggregated metrics and error conditions

Log Format: JSON structured logs with timestamp, level, component, and context
Storage: ./logs/ directory with rotation by date and size

Usage:
    from logger_utils import get_logger, log_rag_retrieval, log_chat_interaction
    
    logger = get_logger("component_name")
    logger.info("User logged in", extra={"user_hash": hash_user_id("user1")})
    
    log_rag_retrieval(
        query_hash=hash_query("original_query"),
        doc_count=5,
        retrieval_time_ms=245.3,
        token_count=1200
    )
"""

import logging
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler


# ============================================================================
# CONFIGURATION
# ============================================================================

LOG_DIR = Path("./logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_LEVEL = logging.INFO
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5


# ============================================================================
# PRIVACY UTILITIES
# ============================================================================

def hash_user_id(user_id: str) -> str:
    """
    Hash a user ID for logging without exposing actual username.

    Args:
        user_id: Original user identifier

    Returns:
        SHA256 hash of user_id
    """
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]


def hash_query(query: str) -> str:
    """
    Hash a query for logging without exposing content.

    Args:
        query: Original user query

    Returns:
        SHA256 hash of query
    """
    return hashlib.sha256(query.encode()).hexdigest()[:12]


def sanitize_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text for logging (never log full conversation text).

    Args:
        text: Text to sanitize
        max_length: Maximum characters to keep

    Returns:
        Sanitized text
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


# ============================================================================
# JSON FORMATTER FOR STRUCTURED LOGS
# ============================================================================

class StructuredJsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in [
                    'name', 'msg', 'args', 'created', 'msecs', 'levelname',
                    'levelno', 'pathname', 'filename', 'module', 'lineno',
                    'funcName', 'getMessage', 'exc_info', 'exc_text', 'stack_info',
                    'relativeCreated', 'thread', 'threadName', 'processName',
                    'process', 'taskName'
                ]:
                    if not key.startswith('_'):
                        log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


# ============================================================================
# LOGGER FACTORY
# ============================================================================

def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with structured JSON formatting.

    Args:
        name: Logger name (typically module name)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)

    # File handler with rotation
    log_file = LOG_DIR / f"{name}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(StructuredJsonFormatter())

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ============================================================================
# PERFORMANCE LOGGING
# ============================================================================

def log_rag_retrieval(
    query_hash: str,
    doc_count: int,
    retrieval_time_ms: float,
    token_count: int,
    vector_store_size: Optional[int] = None
) -> None:
    """
    Log RAG retrieval performance metrics.

    Args:
        query_hash: Hashed user query
        doc_count: Number of documents retrieved
        retrieval_time_ms: Time taken for retrieval (milliseconds)
        token_count: Total tokens in retrieved documents
        vector_store_size: Size of vector store (optional)
    """
    logger = get_logger("rag_performance")

    logger.info(
        "RAG retrieval completed",
        extra={
            "query_hash": query_hash,
            "doc_count": doc_count,
            "retrieval_time_ms": round(retrieval_time_ms, 2),
            "token_count": token_count,
            "vector_store_size": vector_store_size,
            "avg_tokens_per_doc": round(token_count / doc_count, 1) if doc_count > 0 else 0
        }
    )


def log_response_generation(
    query_hash: str,
    response_time_ms: float,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int
) -> None:
    """
    Log response generation performance metrics.

    Args:
        query_hash: Hashed user query
        response_time_ms: Time taken for generation (milliseconds)
        input_tokens: Tokens in prompt
        output_tokens: Tokens in response
        total_tokens: Total tokens used
    """
    logger = get_logger("response_generation")

    logger.info(
        "Response generated",
        extra={
            "query_hash": query_hash,
            "response_time_ms": round(response_time_ms, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        }
    )


def log_end_to_end_latency(
    user_hash: str,
    total_latency_ms: float,
    retrieval_time_ms: float,
    generation_time_ms: float
) -> None:
    """
    Log end-to-end chat interaction latency.

    Args:
        user_hash: Anonymized user identifier
        total_latency_ms: Total time from query to response
        retrieval_time_ms: Time for RAG retrieval
        generation_time_ms: Time for response generation
    """
    logger = get_logger("latency")

    logger.info(
        "Chat interaction completed",
        extra={
            "user_hash": user_hash,
            "total_latency_ms": round(total_latency_ms, 2),
            "retrieval_time_ms": round(retrieval_time_ms, 2),
            "generation_time_ms": round(generation_time_ms, 2),
            "retrieval_ratio": round(retrieval_time_ms / total_latency_ms * 100, 1)
        }
    )


# ============================================================================
# SECURITY & AUDIT LOGGING
# ============================================================================

def log_user_action(
    action: str,
    user_hash: str,
    page: str,
    status: str = "success"
) -> None:
    """
    Log user actions for audit trail.

    Args:
        action: Action name (e.g., "login", "journal_save", "chat_send")
        user_hash: Anonymized user identifier
        page: Page or feature accessed
        status: Action status (success, error, etc.)
    """
    logger = get_logger("audit")

    logger.info(
        f"User action: {action}",
        extra={
            "user_hash": user_hash,
            "action": action,
            "page": page,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    )


def log_api_rate_limit(
    api_name: str,
    retry_count: int,
    wait_time_seconds: float
) -> None:
    """
    Log API rate limiting events.

    Args:
        api_name: Name of API (e.g., "Gemini", "ChromaDB")
        retry_count: Number of retries attempted
        wait_time_seconds: Time waited before retry
    """
    logger = get_logger("api_limits")

    logger.warning(
        f"API rate limit: {api_name}",
        extra={
            "api_name": api_name,
            "retry_count": retry_count,
            "wait_time_seconds": round(wait_time_seconds, 2)
        }
    )


def log_error_event(
    error_type: str,
    error_message: str,
    component: str,
    user_hash: Optional[str] = None
) -> None:
    """
    Log error events for monitoring and debugging.

    Args:
        error_type: Type of error (e.g., "ValidationError", "APIError")
        error_message: Error message (sanitized, no PII)
        component: Component where error occurred
        user_hash: Optional anonymized user identifier
    """
    logger = get_logger("errors")

    logger.error(
        f"{error_type} in {component}",
        extra={
            "error_type": error_type,
            "error_message": sanitize_text(error_message),
            "component": component,
            "user_hash": user_hash
        }
    )


def log_security_event(
    event: str,
    severity: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log security events (failed auth, suspicious activity, etc.).

    Args:
        event: Security event name
        severity: Severity level (low, medium, high, critical)
        details: Additional event details (dict)
    """
    logger = get_logger("security")

    log_level = {
        "low": logging.INFO,
        "medium": logging.WARNING,
        "high": logging.ERROR,
        "critical": logging.CRITICAL
    }.get(severity, logging.WARNING)

    log_data = {
        "event": event,
        "severity": severity,
        "timestamp": datetime.now().isoformat()
    }

    if details:
        log_data.update(details)

    logger.log(log_level, f"Security: {event}", extra=log_data)


# ============================================================================
# SYSTEM HEALTH LOGGING
# ============================================================================

def log_system_health(
    vector_db_size_mb: float,
    user_count: int,
    active_sessions: int,
    avg_latency_ms: float
) -> None:
    """
    Log system health metrics (called periodically).

    Args:
        vector_db_size_mb: Vector database size in MB
        user_count: Total registered users
        active_sessions: Current active sessions
        avg_latency_ms: Average response latency
    """
    logger = get_logger("system_health")

    logger.info(
        "System health report",
        extra={
            "vector_db_size_mb": round(vector_db_size_mb, 2),
            "user_count": user_count,
            "active_sessions": active_sessions,
            "avg_latency_ms": round(avg_latency_ms, 2),
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# LOG ANALYSIS UTILITIES
# ============================================================================

def parse_log_file(log_file: Path) -> list:
    """
    Parse JSON-structured log file into list of dicts.

    Args:
        log_file: Path to log file

    Returns:
        List of log entries (dict)
    """
    entries = []

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return entries

    except Exception as e:
        print(f"Error parsing log file {log_file}: {e}")
        return []


def get_latency_stats(hours: int = 24) -> Dict[str, Any]:
    """
    Get latency statistics from logs.

    Args:
        hours: Hours of historical data to analyze

    Returns:
        Dictionary with latency stats
    """
    latency_log = LOG_DIR / "latency.log"

    if not latency_log.exists():
        return {"message": "No latency data available"}

    entries = parse_log_file(latency_log)

    if not entries:
        return {"message": "No latency entries found"}

    latencies = [e.get("total_latency_ms", 0) for e in entries if "total_latency_ms" in e]

    if not latencies:
        return {"message": "No latency measurements found"}

    return {
        "count": len(latencies),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "avg_ms": sum(latencies) / len(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 1 else latencies[0]
    }


def get_error_summary() -> Dict[str, int]:
    """Get summary of errors from logs."""
    error_log = LOG_DIR / "errors.log"

    if not error_log.exists():
        return {}

    entries = parse_log_file(error_log)
    error_counts = {}

    for entry in entries:
        error_type = entry.get("error_type", "Unknown")
        error_counts[error_type] = error_counts.get(error_type, 0) + 1

    return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))


if __name__ == "__main__":
    # Example usage
    print("Logger Utilities - Example Output\n")

    # Get loggers
    app_logger = get_logger("therapeutic_companion")
    app_logger.info("Application started", extra={"version": "1.0.0"})

    # Log example metrics
    log_rag_retrieval(
        query_hash=hash_query("How can I manage anxiety?"),
        doc_count=5,
        retrieval_time_ms=245.3,
        token_count=1200
    )

    log_response_generation(
        query_hash=hash_query("How can I manage anxiety?"),
        response_time_ms=1850.5,
        input_tokens=450,
        output_tokens=180,
        total_tokens=630
    )

    log_end_to_end_latency(
        user_hash=hash_user_id("user_example@example.com"),
        total_latency_ms=2095.8,
        retrieval_time_ms=245.3,
        generation_time_ms=1850.5
    )

    log_user_action(
        action="journal_save",
        user_hash=hash_user_id("user_example@example.com"),
        page="Activities",
        status="success"
    )

    log_security_event(
        event="successful_login",
        severity="low",
        details={"user_hash": hash_user_id("user_example@example.com")}
    )

    print("\n✅ Example logs written to ./logs/")
    print("\nLatency Statistics:")
    stats = get_latency_stats()
    print(json.dumps(stats, indent=2))
