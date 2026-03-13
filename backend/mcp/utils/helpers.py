"""
Utility Functions for MCP Server
Helper functions for common operations in the MCP server.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPSessionContext(BaseModel):
    """
    Context object for MCP sessions containing user and session information.
    """
    user_id: str
    session_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


def create_session_context(user_id: str, session_id: str,
                         metadata: Optional[Dict[str, Any]] = None) -> MCPSessionContext:
    """
    Create a session context for an MCP session.

    Args:
        user_id: The ID of the authenticated user
        session_id: The unique session identifier
        metadata: Additional metadata for the session

    Returns:
        MCPSessionContext object
    """
    context = MCPSessionContext(
        user_id=user_id,
        session_id=session_id,
        created_at=datetime.utcnow(),
        metadata=metadata or {}
    )
    logger.info(f"Created MCP session context for user {user_id}, session {session_id}")
    return context


def validate_session_context(context: MCPSessionContext) -> bool:
    """
    Validate an MCP session context.

    Args:
        context: The session context to validate

    Returns:
        True if context is valid, False otherwise
    """
    if not context.user_id or not context.session_id:
        logger.warning("Session context missing required fields")
        return False

    if context.expires_at and datetime.utcnow() > context.expires_at:
        logger.warning(f"Session {context.session_id} has expired")
        return False

    logger.debug(f"Validated session context for user {context.user_id}")
    return True


def format_tool_response(success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
    """
    Format a standardized response for MCP tools.

    Args:
        success: Whether the operation was successful
        data: The response data (if successful)
        error: The error message (if failed)

    Returns:
        Formatted response dictionary
    """
    response = {"success": success}

    if success and data is not None:
        response["data"] = data
    elif not success and error is not None:
        response["error"] = error

    logger.debug(f"MCP tool response formatted: success={success}")
    return response


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: The input text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return text

    # Remove potentially dangerous characters/sequences
    sanitized = text.replace('\0', '')  # Null bytes
    sanitized = sanitized.replace('\n', ' ')  # Newlines
    sanitized = sanitized.replace('\r', ' ')  # Carriage returns

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    logger.debug("Input sanitized")
    return sanitized


def extract_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Extract datetime from string representation.

    Args:
        date_str: String representation of a date/time

    Returns:
        Datetime object or None if invalid
    """
    if not date_str:
        return None

    try:
        # Try ISO format first
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            # Try other common formats
            for fmt in [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d'
            ]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass

    logger.warning(f"Could not parse datetime from string: {date_str}")
    return None