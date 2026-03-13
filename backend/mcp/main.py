"""
Main Entry Point for MCP Server
Starts the MCP server with FastAPI integration.
"""

import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from mcp.core.server import get_mcp_app
from mcp.core.config import config, MCP_SERVER_NAME
from core.dependencies import get_current_user
from db.session import get_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPInitializeRequest(BaseModel):
    """
    Request model for initializing an MCP session.
    """
    user_token: str
    session_metadata: Optional[Dict[str, Any]] = None


class MCPInitializeResponse(BaseModel):
    """
    Response model for MCP session initialization.
    """
    success: bool
    session_id: Optional[str] = None
    message: Optional[str] = None


# Create the main FastAPI app with MCP integration
app = get_mcp_app()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS.split(",") if config.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"{MCP_SERVER_NAME} starting up...")
    logger.info(f"Server configured to run on {config.HOST}:{config.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info(f"{MCP_SERVER_NAME} shutting down...")


@app.post("/mcp/initialize")
async def initialize_mcp_session(request: MCPInitializeRequest):
    """
    Initialize an MCP session for a user.
    """
    try:
        # In a real implementation, you would validate the user token
        # and create a session context here
        logger.info(f"Initializing MCP session for user token")

        # Generate a session ID (in real implementation, use proper session management)
        import uuid
        session_id = str(uuid.uuid4())

        # Store session info (in real implementation, use Redis or database)
        # For now, we'll just return the session ID
        return MCPInitializeResponse(
            success=True,
            session_id=session_id,
            message="MCP session initialized successfully"
        )
    except Exception as e:
        logger.error(f"Error initializing MCP session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/session/{session_id}")
async def get_session_info(session_id: str, current_user: str = Depends(get_current_user)):
    """
    Get information about an MCP session.
    """
    try:
        # In a real implementation, you would validate the session
        # and ensure it belongs to the current user
        logger.info(f"Getting session info for session {session_id}")

        # Mock session info
        return {
            "session_id": session_id,
            "user_id": current_user,
            "status": "active",
            "created_at": "2023-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/mcp/session/{session_id}")
async def close_session(session_id: str, current_user: str = Depends(get_current_user)):
    """
    Close an MCP session.
    """
    try:
        # In a real implementation, you would close the session
        # and clean up resources
        logger.info(f"Closing session {session_id}")

        # Mock session closure
        return {"message": f"Session {session_id} closed successfully"}
    except Exception as e:
        logger.error(f"Error closing session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """
    Root endpoint for the MCP server.
    """
    return {
        "message": "Todo AI Chatbot MCP Server",
        "version": "1.0.0",
        "status": "running",
        "server_name": MCP_SERVER_NAME
    }


def run_server():
    """
    Run the MCP server using uvicorn.
    """
    logger.info(f"Starting {MCP_SERVER_NAME} on {config.HOST}:{config.PORT}")

    uvicorn.run(
        "mcp.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info" if not config.DEBUG else "debug"
    )


if __name__ == "__main__":
    # Run the server when executed directly
    run_server()