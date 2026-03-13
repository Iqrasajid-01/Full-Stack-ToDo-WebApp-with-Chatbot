#!/usr/bin/env python3
"""
Setup script for MCP Server
Installs and sets up the MCP server for the Todo AI Chatbot system.
"""

import os
import sys
import subprocess
from pathlib import Path


def install_dependencies():
    """Install the required dependencies for the MCP server."""
    print("Installing MCP server dependencies...")

    requirements_path = Path(__file__).parent / "requirements.txt"

    try:
        # Install requirements using pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
        ], check=True, capture_output=True, text=True)

        print("Dependencies installed successfully!")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def setup_database():
    """Setup the database for the MCP server."""
    print("Setting up database for MCP server...")

    # The MCP server uses the same database as the main application
    # so we just need to ensure the tables exist
    try:
        from db.init import create_db_and_tables
        create_db_and_tables()
        print("Database setup completed successfully!")
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)


def verify_installation():
    """Verify that the MCP server is properly installed."""
    print("Verifying MCP server installation...")

    try:
        # Try importing the main modules
        import mcp
        from mcp.core.server import get_mcp_app
        from mcp.tools.task_tools import add_task_tool
        from mcp.utils.helpers import create_session_context

        print("MCP server modules imported successfully!")
        return True

    except ImportError as e:
        print(f"Error importing MCP server modules: {e}")
        return False


def main():
    """Main setup function."""
    print("Setting up MCP Server for Todo AI Chatbot System...")

    # Change to the backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)

    # Install dependencies
    install_dependencies()

    # Setup database
    setup_database()

    # Verify installation
    if verify_installation():
        print("\nMCP Server setup completed successfully!")
        print("\nTo start the MCP server, run:")
        print("  cd backend")
        print("  python -m mcp.main")
        print("\nOr use uvicorn:")
        print("  cd backend")
        print("  uvicorn mcp.main:app --reload --port 3001")
    else:
        print("\nMCP Server setup completed with warnings.")
        print("Some components may not be working properly.")


if __name__ == "__main__":
    main()