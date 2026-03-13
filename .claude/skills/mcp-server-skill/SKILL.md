---
name: mcp-server-skill
description: Set up and manage the MCP (Model Context Protocol) server for the Todo AI Chatbot system, enabling AI agents to interact with Todo application functionality through MCP tools.
---

# MCP Server Skill

## Instructions

1. **MCP Server Setup**
   - Create MCP server using Official MCP SDK in Python
   - Integrate MCP server with FastAPI backend
   - Define MCP tool registration system
   - Ensure stateless architecture
   - Connect MCP server with Neon PostgreSQL database using SQLModel

2. **Tool Implementation**
   - Expose required Todo tools: add_task, list_tasks, complete_task, delete_task, update_task
   - Implement proper error handling and validation for all tools
   - Ensure tools follow consistent API contracts
   - Support proper user isolation and authentication

3. **Database Integration**
   - Use SQLModel for database operations
   - Implement secure database access patterns
   - Follow ACID transaction principles
   - Ensure proper connection pooling and resource management

4. **Architecture & Organization**
   - Implement clean modular structure
   - Separate tool definitions from server implementation
   - Create reusable components and utilities
   - Follow production-grade coding standards

## Best Practices
- Ensure production-grade architecture with proper error handling
- Maintain clean separation of concerns in code organization
- Implement secure database access with proper user isolation
- Optimize for fast response times and efficient resource usage
- Ensure full compatibility with OpenAI Agents SDK
- Follow stateless design principles for scalability
- Use environment variables for configuration and secrets
- Implement proper logging and observability

Use this skill when implementing MCP server, tool registration, or MCP backend architecture.