"""
Configuration for MCP Server
Settings and constants for the MCP server.
"""

import os
from typing import Optional
from pydantic import BaseModel


class MCPConfig(BaseModel):
    """
    Configuration settings for the MCP server.
    """
    # Server settings
    HOST: str = os.getenv("MCP_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("MCP_PORT", "3001"))
    DEBUG: bool = os.getenv("MCP_DEBUG", "false").lower() == "true"

    # Database settings
    DB_POOL_SIZE: int = int(os.getenv("MCP_DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("MCP_DB_MAX_OVERFLOW", "10"))
    DB_POOL_RECYCLE: int = int(os.getenv("MCP_DB_POOL_RECYCLE", "300"))

    # Tool settings
    DEFAULT_TASK_LIMIT: int = int(os.getenv("MCP_DEFAULT_TASK_LIMIT", "50"))
    MAX_TASK_LIMIT: int = int(os.getenv("MCP_MAX_TASK_LIMIT", "100"))
    SESSION_TIMEOUT: int = int(os.getenv("MCP_SESSION_TIMEOUT", "3600"))  # 1 hour

    # Rate limiting
    REQUESTS_PER_MINUTE: int = int(os.getenv("MCP_REQUESTS_PER_MINUTE", "60"))

    # Security
    ENABLE_SSL: bool = os.getenv("MCP_ENABLE_SSL", "false").lower() == "true"
    CORS_ORIGINS: str = os.getenv("MCP_CORS_ORIGINS", "*")


# Create config instance
config = MCPConfig()


def get_config() -> MCPConfig:
    """
    Get the MCP configuration instance.

    Returns:
        MCPConfig instance
    """
    return config


# Constants
MCP_SERVER_NAME = "todo-mcp-server"
MCP_PROTOCOL_VERSION = "1.0.0"
MCP_API_VERSION = "1.0.0"

# Tool names
TOOL_ADD_TASK = "add_task"
TOOL_LIST_TASKS = "list_tasks"
TOOL_COMPLETE_TASK = "complete_task"
TOOL_DELETE_TASK = "delete_task"
TOOL_UPDATE_TASK = "update_task"

# Priority levels
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_CRITICAL = "critical"

SUPPORTED_PRIORITIES = [PRIORITY_LOW, PRIORITY_MEDIUM, PRIORITY_HIGH, PRIORITY_CRITICAL]