# MCP Server for Todo AI Chatbot

The Model Context Protocol (MCP) server enables AI agents to interact with the Todo application functionality through standardized tools.

## Overview

The MCP server provides a bridge between AI agents and the Todo application, allowing AI systems to perform operations like:
- Adding new tasks
- Listing existing tasks
- Completing tasks
- Updating task information
- Deleting tasks

## Architecture

The MCP server follows a modular architecture:

```
mcp/
├── main.py                 # Main entry point
├── core/
│   ├── server.py          # MCP server implementation
│   └── config.py          # Configuration settings
├── tools/
│   └── task_tools.py      # Task operation implementations
├── utils/
│   └── helpers.py         # Utility functions
└── requirements.txt       # Dependencies
```

## Features

- **Production-grade architecture**: Built with FastAPI and SQLAlchemy
- **Secure database access**: Proper user isolation and authentication
- **Modular structure**: Clean separation of concerns
- **Fast response times**: Optimized for AI agent interactions
- **OpenAI Agents SDK compatible**: Full compatibility with OpenAI's agent framework

## Available Tools

The MCP server exposes the following tools:

### `add_task`
Add a new task to the user's todo list.

Parameters:
- `title`: Task title (required)
- `description`: Task description (optional)
- `priority`: Task priority (default: "medium")
- `due_date`: Due date in ISO format (optional)

### `list_tasks`
List tasks from the user's todo list.

Parameters:
- `completed`: Filter by completion status (optional)
- `limit`: Maximum number of tasks to return (default: 50)
- `skip`: Number of tasks to skip (default: 0)

### `complete_task`
Mark a task as completed or incomplete.

Parameters:
- `task_id`: ID of the task to update
- `completed`: Whether to mark as completed (default: true)

### `delete_task`
Delete a task from the user's todo list.

Parameters:
- `task_id`: ID of the task to delete

### `update_task`
Update a task's information.

Parameters:
- `task_id`: ID of the task to update
- `title`: New title (optional)
- `description`: New description (optional)
- `priority`: New priority (optional)
- `due_date`: New due date (optional)

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install MCP server dependencies:
```bash
python -m mcp.setup
```

## Running the Server

Start the MCP server:

```bash
cd backend
python -m mcp.main
```

Or use uvicorn directly:
```bash
cd backend
uvicorn mcp.main:app --reload --port 3001
```

The server will be available at `http://localhost:3001`.

## Integration with AI Agents

The MCP server is designed to work seamlessly with AI agents that support the Model Context Protocol. The tools are registered with proper type hints and documentation to enable AI agents to understand their functionality.

## Security

- User isolation: Each user can only access their own tasks
- Authentication: Requires valid user session
- Input sanitization: All inputs are validated and sanitized
- Rate limiting: Prevents abuse of the API

## Configuration

The server can be configured using environment variables:

- `MCP_HOST`: Host address (default: "127.0.0.1")
- `MCP_PORT`: Port number (default: 3001)
- `MCP_DEBUG`: Enable debug mode (default: false)
- `MCP_DEFAULT_TASK_LIMIT`: Default task limit for list operations
- `MCP_MAX_TASK_LIMIT`: Maximum allowed task limit
- `MCP_SESSION_TIMEOUT`: Session timeout in seconds
- `MCP_REQUESTS_PER_MINUTE`: Rate limit for requests

## Database Integration

The MCP server uses the same database connection as the main application, leveraging the existing SQLAlchemy setup with Neon PostgreSQL and SQLModel integration.

## Error Handling

All MCP tools implement comprehensive error handling with proper error messages returned to AI agents for better debugging and recovery.