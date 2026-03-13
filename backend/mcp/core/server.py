"""
MCP (Model Context Protocol) Server for Todo AI Chatbot System
This module creates an MCP server that enables AI agents to interact with Todo application functionality.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from mcp.server import Server
from mcp.types import TextContent, Diagnostic, ErrorCode
from sqlalchemy.orm import Session

from models.task import TaskCreate, TaskUpdate, TaskRead
from db.session import get_session
from core.dependencies import get_current_user
from mcp.tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp_server = Server("todo-mcp-server")

# Store active sessions (in production, use Redis or database)
active_sessions: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for the FastAPI application."""
    # Startup
    logger.info("Starting MCP server...")

    # Register MCP tools
    await register_mcp_tools()

    yield

    # Shutdown
    logger.info("Shutting down MCP server...")


async def register_mcp_tools():
    """Register all MCP tools with the server."""
    logger.info("Registering MCP tools...")

    # Register add_task tool
    @mcp_server.tool("add_task")
    async def handle_add_task(context: Dict[str, Any], title: str, description: Optional[str] = None,
                             priority: str = "medium", due_date: Optional[str] = None) -> Dict[str, Any]:
        """Add a new task to the user's todo list."""
        try:
            user_id = context.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User not authenticated")

            # Prepare task data
            task_data = TaskCreate(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date
            )

            # Get database session
            session_gen = get_session()
            session: Session = next(session_gen)

            try:
                # Call the actual implementation
                result = await add_task_tool(user_id, task_data, session)
                return {"success": True, "task": result.model_dump()}
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error in add_task: {str(e)}")
            return {"success": False, "error": str(e)}

    # Register list_tasks tool
    @mcp_server.tool("list_tasks")
    async def handle_list_tasks(context: Dict[str, Any], completed: Optional[bool] = None,
                               limit: int = 50, skip: int = 0) -> Dict[str, Any]:
        """List tasks from the user's todo list."""
        try:
            user_id = context.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User not authenticated")

            # Get database session
            session_gen = get_session()
            session: Session = next(session_gen)

            try:
                # Call the actual implementation
                result = await list_tasks_tool(user_id, completed, limit, skip, session)
                return {"success": True, "tasks": [task.model_dump() for task in result]}
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error in list_tasks: {str(e)}")
            return {"success": False, "error": str(e)}

    # Register complete_task tool
    @mcp_server.tool("complete_task")
    async def handle_complete_task(context: Dict[str, Any], task_id: int,
                                  completed: bool = True) -> Dict[str, Any]:
        """Complete or uncomplete a task."""
        try:
            user_id = context.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User not authenticated")

            # Get database session
            session_gen = get_session()
            session: Session = next(session_gen)

            try:
                # Call the actual implementation
                result = await complete_task_tool(user_id, task_id, completed, session)
                return {"success": True, "task": result.model_dump()}
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error in complete_task: {str(e)}")
            return {"success": False, "error": str(e)}

    # Register delete_task tool
    @mcp_server.tool("delete_task")
    async def handle_delete_task(context: Dict[str, Any], task_id: int) -> Dict[str, Any]:
        """Delete a task from the user's todo list."""
        try:
            user_id = context.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User not authenticated")

            # Get database session
            session_gen = get_session()
            session: Session = next(session_gen)

            try:
                # Call the actual implementation
                result = await delete_task_tool(user_id, task_id, session)
                return {"success": True, "deleted": result}
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error in delete_task: {str(e)}")
            return {"success": False, "error": str(e)}

    # Register update_task tool
    @mcp_server.tool("update_task")
    async def handle_update_task(context: Dict[str, Any], task_id: int,
                                title: Optional[str] = None,
                                description: Optional[str] = None,
                                priority: Optional[str] = None,
                                due_date: Optional[str] = None) -> Dict[str, Any]:
        """Update a task in the user's todo list."""
        try:
            user_id = context.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="User not authenticated")

            # Prepare update data
            task_update = TaskUpdate(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date
            )

            # Get database session
            session_gen = get_session()
            session: Session = next(session_gen)

            try:
                # Call the actual implementation
                result = await update_task_tool(user_id, task_id, task_update, session)
                return {"success": True, "task": result.model_dump()}
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Error in update_task: {str(e)}")
            return {"success": False, "error": str(e)}

    logger.info("All MCP tools registered successfully")


def get_mcp_app() -> FastAPI:
    """Create and return the FastAPI application with MCP server integrated."""
    app = FastAPI(
        title="Todo AI Chatbot MCP Server",
        description="MCP server for enabling AI agents to interact with Todo application functionality",
        version="1.0.0",
        lifespan=lifespan
    )

    # Include the MCP server routes
    # In a real implementation, you'd mount the MCP server routes here
    # For now, we'll just return the app

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "mcp-server"}

    return app


# For standalone MCP server (if needed separately from FastAPI)
async def run_mcp_server():
    """Run the MCP server standalone."""
    logger.info("Starting MCP server on port 3001...")

    # This would typically run the MCP server on a specific port
    # await mcp_server.run_tcp("127.0.0.1", 3001)

    # For now, we'll just simulate the server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("MCP server stopped")


if __name__ == "__main__":
    # Run the MCP server standalone
    asyncio.run(run_mcp_server())