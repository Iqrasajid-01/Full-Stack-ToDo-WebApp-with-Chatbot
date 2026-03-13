"""
Tests for MCP Server
Unit and integration tests for the MCP server functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from mcp.core.server import get_mcp_app
from mcp.tools.task_tools import (
    add_task_tool, list_tasks_tool, complete_task_tool,
    delete_task_tool, update_task_tool
)
from models.task import TaskCreate, TaskUpdate, TaskRead


@pytest.fixture
def test_client():
    """Create a test client for the MCP server."""
    app = get_mcp_app()
    return TestClient(app)


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    session = MagicMock()
    return session


@pytest.mark.asyncio
async def test_add_task_tool():
    """Test the add_task_tool function."""
    # Mock session
    session = MagicMock()

    # Create test task data
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        priority="high",
        due_date=datetime.now()
    )

    # Mock the session operations
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = "test_user"
    mock_task.title = "Test Task"
    mock_task.description = "Test Description"
    mock_task.completed = False
    mock_task.priority = "high"
    mock_task.due_date = datetime.now()
    mock_task.created_at = datetime.now()
    mock_task.updated_at = datetime.now()
    mock_task.last_modified_by = "test_user"

    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock(return_value=mock_task)

    # Call the function
    result = await add_task_tool("test_user", task_data, session)

    # Assertions
    assert isinstance(result, TaskRead)
    assert result.title == "Test Task"
    assert result.user_id == "test_user"
    session.add.assert_called_once()
    session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_list_tasks_tool(mock_session):
    """Test the list_tasks_tool function."""
    # Mock tasks
    mock_task1 = MagicMock()
    mock_task1.id = 1
    mock_task1.user_id = "test_user"
    mock_task1.title = "Task 1"
    mock_task1.description = "Description 1"
    mock_task1.completed = False
    mock_task1.priority = "medium"
    mock_task1.created_at = datetime.now()

    mock_task2 = MagicMock()
    mock_task2.id = 2
    mock_task2.user_id = "test_user"
    mock_task2.title = "Task 2"
    mock_task2.description = "Description 2"
    mock_task2.completed = True
    mock_task2.priority = "high"
    mock_task2.created_at = datetime.now()

    # Mock query
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [mock_task1, mock_task2]

    mock_session.query.return_value = mock_query

    # Call the function
    result = await list_tasks_tool("test_user", None, 50, 0, mock_session)

    # Assertions
    assert len(result) == 2
    assert all(isinstance(task, TaskRead) for task in result)
    assert result[0].title == "Task 1"
    assert result[1].title == "Task 2"


@pytest.mark.asyncio
async def test_complete_task_tool(mock_session):
    """Test the complete_task_tool function."""
    # Mock task
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = "test_user"
    mock_task.title = "Test Task"
    mock_task.completed = False
    mock_task.priority = "medium"
    mock_task.created_at = datetime.now()

    # Mock query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_task
    mock_session.query.return_value = mock_query

    # Call the function
    result = await complete_task_tool("test_user", 1, True, mock_session)

    # Assertions
    assert isinstance(result, TaskRead)
    assert result.completed is True
    assert result.title == "Test Task"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_task_tool(mock_session):
    """Test the delete_task_tool function."""
    # Mock task
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = "test_user"

    # Mock query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_task
    mock_session.query.return_value = mock_query

    # Call the function
    result = await delete_task_tool("test_user", 1, mock_session)

    # Assertions
    assert result is True
    mock_session.delete.assert_called_once_with(mock_task)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_task_tool(mock_session):
    """Test the update_task_tool function."""
    # Mock task
    mock_task = MagicMock()
    mock_task.id = 1
    mock_task.user_id = "test_user"
    mock_task.title = "Old Title"
    mock_task.description = "Old Description"
    mock_task.completed = False
    mock_task.priority = "low"
    mock_task.created_at = datetime.now()

    # Mock query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_task
    mock_session.query.return_value = mock_query

    # Create update data
    task_update = TaskUpdate(
        title="New Title",
        description="New Description",
        priority="high"
    )

    # Call the function
    result = await update_task_tool("test_user", 1, task_update, mock_session)

    # Assertions
    assert isinstance(result, TaskRead)
    assert result.title == "New Title"
    assert result.description == "New Description"
    assert result.priority == "high"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_health_endpoint(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "mcp-server"


def test_root_endpoint(test_client):
    """Test the root endpoint."""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Todo AI Chatbot MCP Server" in data["message"]