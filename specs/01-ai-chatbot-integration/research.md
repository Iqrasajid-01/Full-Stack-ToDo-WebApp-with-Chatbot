# Research: AI Chatbot Integration

**Feature**: AI-Native Todo SaaS Chatbot using Cohere + OpenAI Agents SDK
**Date**: 2026-02-17
**Purpose**: Resolve technical unknowns and establish best practices for implementation

---

## 1. Cohere API Integration

### Decision: Use Cohere Chat API with command-r-plus model

**Rationale**:
- command-r-plus is Cohere's most capable model for tool use and reasoning
- Chat API provides built-in conversation management
- Supports tool calling natively with structured outputs
- Optimized for enterprise RAG and tool use scenarios
- Better performance on multi-turn conversations compared to base command-r

**API Endpoints**:
- `POST https://api.cohere.ai/v1/chat` - Main chat endpoint
- Headers: `Authorization: Bearer {COHERE_API_KEY}`, `Content-Type: application/json`
- Key parameters: `message`, `model`, `chat_history`, `tools`, `temperature`

**Message Format**:
```json
{
  "message": "Add a task to buy groceries",
  "model": "command-r-plus",
  "chat_history": [
    {"role": "USER", "message": "Hello"},
    {"role": "CHATBOT", "message": "Hi! How can I help?"}
  ],
  "tools": [
    {
      "name": "add_task",
      "description": "Add a new task",
      "parameter_definitions": {
        "title": {"type": "string", "description": "Task title"}
      }
    }
  ]
}
```

**Tool Calling**:
- Cohere returns `tool_calls` array in response when tools are needed
- Each tool call includes `name` and `parameters`
- Application must execute tool and return result via `tool_responses`
- Model generates final response after tool execution

**Alternatives Considered**:
- **command-r**: Lighter weight but less capable on complex reasoning
- **command-nightly**: Latest model but less stable for production
- **Direct API vs SDK**: Using direct REST API for maximum control

**Best Practices**:
- Store chat history in database for conversation continuity
- Use `temperature=0.3` for consistent, deterministic responses
- Implement retry logic with exponential backoff (3 retries max)
- Cache frequent responses to reduce API calls
- Monitor token usage and implement rate limiting

**References**:
- https://docs.cohere.com/reference/chat
- https://docs.cohere.com/docs/command-r

---

## 2. OpenAI Agents SDK Architecture

### Decision: Use OpenAI Agents SDK with custom Cohere adapter

**Rationale**:
- Provides structured agent orchestration framework
- Built-in support for tool-based architecture
- Manages conversation context and state
- Separates agent logic from LLM implementation
- Allows swapping LLM providers via adapter pattern

**Core Components**:

**Agent**:
- Defines the AI agent's behavior and capabilities
- Configured with system instructions and available tools
- Stateless execution - each request creates new agent instance

**Runner**:
- Orchestrates agent execution
- Manages message flow between user, agent, and tools
- Handles tool invocation and response aggregation
- Maintains conversation context across turns

**Context**:
- Stores conversation state and user information
- Includes: user_id, project_id, session state, loaded tasks
- Persisted in database between requests
- Passed to agent for informed decision-making

**Tools**:
- Functions exposed to the agent
- Each tool has name, description, and parameter schema
- Tools call FastAPI endpoints (not direct database access)
- Return structured JSON responses

**Adapter Pattern**:
```python
class CohereAgentModel:
    def __init__(self, api_key: str, model: str = "command-r-plus"):
        self.api_key = api_key
        self.model = model
        self.client = cohere.Client(api_key)
    
    async def send_message(self, messages: list, context: dict, tools: list) -> AgentResponse:
        # Translate Agent messages → Cohere format
        cohere_messages = self._translate_messages(messages)
        cohere_tools = self._translate_tools(tools)
        
        # Call Cohere Chat API
        response = await self.client.chat(
            message=messages[-1].content,
            chat_history=cohere_messages[:-1],
            tools=cohere_tools,
            model=self.model
        )
        
        # Parse Cohere response → Agent format
        return self._parse_response(response)
    
    def _translate_messages(self, messages: list) -> list:
        # Convert Agent message format to Cohere format
        pass
    
    def _parse_response(self, response) -> AgentResponse:
        # Convert Cohere response to Agent format
        pass
```

**Alternatives Considered**:
- **Direct Cohere API**: Would require building agent orchestration from scratch
- **LangChain**: More complex, heavier dependency, overkill for this use case
- **Custom agent framework**: Reinventing wheel, less maintainable

**Best Practices**:
- Keep agent stateless - persist all state in database
- Use dependency injection for tools and context
- Implement tool execution timeouts (30s max)
- Log all agent decisions for debugging
- Version agent configurations for rollback capability

**References**:
- https://github.com/openai/agents-sdk
- https://openai.github.io/agents-sdk/

---

## 3. MCP (Model Context Protocol) Server

### Decision: Implement MCP server with 5 task management tools

**Rationale**:
- Constitution mandates AI tools execute only through MCP (Principle IV)
- Standardized tool interface for AI agents
- Enforces separation between AI and database
- Provides security layer for user isolation
- Enables tool versioning and evolution

**Tool Definitions**:

**add_task**:
```python
@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "", due_date: datetime = None) -> dict:
    """Add a new task for the authenticated user."""
    # Validate user_id matches JWT token
    # Create task via FastAPI endpoint or direct SQLModel
    # Return created task with id
```

**list_tasks**:
```python
@mcp.tool()
async def list_tasks(user_id: str, status: str = "all", limit: int = 50) -> list:
    """List tasks for the authenticated user with optional filtering."""
    # Validate user_id
    # Query tasks with user_id filter (enforces isolation)
    # Return list of tasks with id, title, status, due_date
```

**complete_task**:
```python
@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> dict:
    """Mark a task as completed."""
    # Validate user_id owns task_id
    # Update task status to 'completed'
    # Return updated task
```

**delete_task**:
```python
@mcp.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task."""
    # Validate user_id owns task_id
    # Delete task from database
    # Return success confirmation
```

**update_task**:
```python
@mcp.tool()
async def update_task(user_id: str, task_id: int, title: str = None, description: str = None, due_date: datetime = None) -> dict:
    """Update task details."""
    # Validate user_id owns task_id
    # Update only provided fields
    # Return updated task
```

**Security Enforcement**:
- Every tool validates user_id against JWT token
- SQLModel queries always include user_id filter
- Return 403 if user attempts to access another user's task
- Log all tool invocations for audit trail

**Error Handling**:
- Catch and wrap database errors
- Return structured error responses
- Never expose internal error details to user
- Implement tool execution timeouts

**Alternatives Considered**:
- **Direct FastAPI endpoints**: Would bypass MCP layer, violate constitution
- **GraphQL mutations**: More complex, MCP provides simpler tool interface
- **RPC-style calls**: MCP provides better standardization

**Best Practices**:
- Tools are pure functions - no side effects beyond database operations
- Validate all inputs before database operations
- Use SQLModel transactions for data integrity
- Implement tool-level rate limiting
- Document tool contracts in OpenAPI/YAML format

**References**:
- https://modelcontextprotocol.io/
- https://github.com/modelcontextprotocol

---

## 4. Conversation Persistence

### Decision: Store conversations and messages in PostgreSQL with SQLModel

**Rationale**:
- Constitution mandates stateless backend with DB-backed state (Principle II)
- PostgreSQL already in use for Todo application
- SQLModel provides type-safe ORM layer
- Enables conversation continuity across sessions
- Supports conversation history for agent context

**Database Schema**:

**Conversation Table**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(..., index=True)  # JWT user identifier
    title: str = Field(default="New Conversation")  # Auto-generated or user-provided
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Message Table**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(..., foreign_key="conversations.id", index=True)
    user_id: str = Field(..., index=True)  # Denormalized for quick filtering
    role: str = Field(...)  # "user" or "assistant"
    content: str = Field(..., sa_column=Column(String))  # Full message content
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    tool_calls: Optional[dict] = Field(default=None)  # JSON of tool calls if any
    
    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Session Management**:
- Each request is stateless (Constitution Principle II)
- Load conversation history from database on each request
- Store new messages after processing
- No in-memory session storage
- Conversation ID passed in request/response

**Query Optimization**:
- Index on user_id for fast user filtering
- Index on conversation_id for message retrieval
- Index on created_at for chronological ordering
- Limit message history to last 50 messages per request
- Implement pagination for long conversations

**Alternatives Considered**:
- **Redis for sessions**: Would violate stateless principle, adds infrastructure
- **In-memory storage**: Violates Constitution Principle II
- **Separate conversations database**: Unnecessary complexity, Neon scales well

**Best Practices**:
- Always filter by user_id to enforce isolation
- Use database transactions for message writes
- Implement soft deletes for conversation archival
- Add updated_at trigger for conversation activity tracking
- Consider partitioning for large conversation tables

---

## 5. JWT Authentication for Chat Endpoints

### Decision: Use Better Auth JWT with FastAPI dependency injection

**Rationale**:
- Existing Todo app uses Better Auth for frontend authentication
- JWT tokens already issued to authenticated users
- Constitution mandates JWT validation on all requests (Principle III)
- FastAPI dependencies provide clean authentication abstraction

**Token Flow**:
1. User logs in via Better Auth (frontend)
2. Better Auth issues JWT with user_id in payload
3. Frontend stores JWT (httpOnly cookie or memory)
4. Frontend sends JWT in `Authorization: Bearer {token}` header
5. FastAPI validates JWT signature and expiration
6. Extract user_id from JWT payload
7. Pass user_id to MCP tools for isolation enforcement

**FastAPI Dependency**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract and validate JWT token, return user_id."""
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")  # or "user_id" depending on token structure
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Usage in route
@router.post("/chatbot/message")
async def chatbot_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    # user_id is guaranteed to be authenticated
```

**User Isolation in MCP Tools**:
```python
@mcp.tool()
async def list_tasks(user_id: str, limit: int = 50) -> list:
    # user_id comes from authenticated JWT
    # Query always filters by user_id
    tasks = await session.exec(
        select(Task).where(Task.user_id == user_id).limit(limit)
    )
    return tasks.all()
```

**Security Measures**:
- Validate JWT signature using HMAC with JWT_SECRET
- Check token expiration on every request
- Never trust user_id from request body - always use JWT-extracted value
- Return 401 for missing/invalid tokens
- Return 403 for cross-user access attempts
- Log all authentication failures

**Alternatives Considered**:
- **Session-based auth**: Would require server-side session storage
- **API keys**: Less secure, doesn't provide user context
- **OAuth2 flow**: Overkill for this use case, Better Auth already in place

**Best Practices**:
- Store JWT_SECRET in environment variable, never in code
- Use HTTPS in production to protect token in transit
- Implement token refresh mechanism for long sessions
- Set reasonable token expiration (e.g., 24 hours)
- Rotate JWT_SECRET periodically

---

## 6. Error Handling Patterns

### Decision: Implement layered error handling with user-friendly messages

**Error Categories**:

**Authentication Errors** (401):
- Invalid or missing JWT token
- Expired token
- Handled by FastAPI dependency

**Authorization Errors** (403):
- User attempts to access another user's task
- MCP tool enforces isolation

**Cohere API Errors**:
- Rate limiting (429): Implement exponential backoff
- Invalid request (400): Log and return generic error
- Service unavailable (503): Return "AI service temporarily unavailable"

**Database Errors**:
- Connection failures: Retry with exponential backoff
- Constraint violations: Return validation error
- Query timeouts: Return "Request timeout, please try again"

**Tool Execution Errors**:
- Invalid parameters: Return "I couldn't understand that. Could you rephrase?"
- Tool not found: Log error, return "Something went wrong"
- Execution timeout: Return "That's taking longer than expected"

**Error Response Format**:
```json
{
  "error": {
    "code": "task_not_found",
    "message": "I couldn't find a task with that description.",
    "details": {}  // Empty in production, populated in development
  }
}
```

**Logging Strategy**:
- Log all errors with full stack traces (server-side only)
- Log user_id, conversation_id for debugging
- Never log JWT tokens or sensitive data
- Use structured logging (JSON format)
- Implement log levels: DEBUG, INFO, WARNING, ERROR

---

## 7. Performance Optimization

### Decision: Async operations throughout with connection pooling

**Database**:
- Use async SQLModel session
- Connection pool: min 5, max 20 connections
- Query timeout: 30 seconds
- Index all foreign keys and filter columns

**Cohere API**:
- Async HTTP client (httpx)
- Request timeout: 30 seconds
- Retry with exponential backoff: 1s, 2s, 4s
- Circuit breaker: Open after 5 consecutive failures

**Frontend**:
- Optimistic UI updates for task operations
- Loading indicators during API calls
- Debounce rapid message sends (300ms)
- Virtual scrolling for long message histories

**Caching**:
- Cache task list for 5 seconds (reduces database load)
- Cache conversation metadata (title, created_at)
- No caching for sensitive user data

**Performance Targets**:
- Chatbot response: < 5s (p95)
- Task operations: < 2s (p95)
- Conversation load: < 2s (p95)
- Concurrent users: 100 without degradation

---

## Summary of Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Provider | Cohere command-r-plus | Best tool use capabilities, enterprise-grade |
| Agent Framework | OpenAI Agents SDK | Structured orchestration, adapter pattern |
| Tool Interface | MCP server | Constitution requirement, clean separation |
| Storage | PostgreSQL + SQLModel | Existing infrastructure, type-safe ORM |
| Authentication | Better Auth JWT | Existing auth system, stateless |
| Error Handling | Layered with user-friendly messages | Better UX, debuggability |
| Performance | Async throughout | Meets performance targets |

All technical unknowns resolved. Ready for Phase 1 design.
