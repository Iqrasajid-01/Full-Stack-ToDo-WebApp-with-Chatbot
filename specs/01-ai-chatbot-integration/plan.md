# Implementation Plan: AI-Native Todo SaaS Chatbot using Cohere + OpenAI Agents SDK

**Branch**: `2-ai-chatbot-integration` | **Date**: 2026-02-17 | **Spec**: [spec.md](../01-ai-chatbot-integration/spec.md)
**Input**: User description: Build a production-grade AI chatbot system integrated into the Todo SaaS that allows users to interact conversationally with their tasks using Cohere LLM and OpenAI Agents SDK architecture.

## Summary

Design and implement a production-grade AI chatbot that integrates into the existing Todo SaaS application, enabling users to manage tasks through natural language conversations. The chatbot uses Cohere API as the LLM provider with OpenAI Agents SDK for agent orchestration, MCP server for tool exposure, and FastAPI backend for chat endpoint and agent execution. All task operations occur through MCP tools that enforce strict user isolation and integrate with the existing Neon PostgreSQL database.

## Technical Context

**Language/Version**: Python 3.11+, TypeScript 5+, Next.js 16+
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK, Cohere API, MCP (Model Context Protocol), Next.js, ChatKit
**Storage**: Neon Serverless PostgreSQL (existing Todo database)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web application (frontend + backend integration)
**Performance Goals**: Chatbot responses within 5 seconds (p95), task operations complete within 2 seconds, conversation history loads within 2 seconds, support 100 concurrent users without degradation
**Constraints**: <5s response time for chatbot messages, <2s for task operations, stateless backend execution, JWT authentication required on all requests, no direct database access from agent
**Scale/Scope**: AI-Native Todo SaaS with conversational task management, supporting create/list/complete/delete/update tasks via natural language

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Spec-Driven Development Only**: All chatbot features originate from specification → plan → tasks → implementation. No manual coding outside spec-driven agent execution.
- [x] **Stateless Backend Architecture**: FastAPI backend remains stateless. All chat state persisted in Neon PostgreSQL. No in-memory conversation storage.
- [x] **Secure Multi-User Isolation**: Each user accesses only their own tasks. All MCP tool calls enforce authenticated user ID verification via JWT tokens from Better Auth.
- [x] **AI Tool-Based Execution Only**: AI agent never directly modifies database. All task operations occur exclusively through MCP tools.
- [x] **Cohere API as LLM Provider**: Cohere API used as primary language model. API key stored securely in environment variable, never exposed in frontend or logs.
- [x] **Agentic Dev Stack Workflow**: Follow spec → plan → tasks → implementation via agents.
- [x] **Technology Standards Compliance**: Next.js frontend, FastAPI backend, SQLModel ORM, Neon PostgreSQL, BetterAuth JWT, OpenAI Agents SDK, MCP server.
- [x] **Agent Responsibilities**: Proper agent assignment (ai-agent-engineer, mcp-server-engineer, chat-backend-engineer, chat-frontend-engineer, etc.)
- [x] **Governance**: All implementation via agents/skills using Claude Code and Spec-Kit Plus. Decisions traceable through specs/ADRs.

## Project Structure

### Documentation (this feature)

```text
specs/01-ai-chatbot-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (Cohere adapter, Agents SDK patterns, MCP best practices)
├── data-model.md        # Phase 1 output (Conversation, Message entities)
├── quickstart.md        # Phase 1 output (Local development setup)
├── contracts/           # Phase 1 output (Chat API schema, MCP tool contracts)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoints
│   └── mcp-tools.yaml   # MCP tool interface definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── main.py                          # FastAPI entry point (existing)
├── app/
│   └── chatbot/                     # NEW: Chatbot module
│       ├── __init__.py
│       ├── agent.py                 # OpenAI Agents SDK agent implementation
│       ├── cohere_adapter.py        # Cohere API adapter for Agents SDK
│       ├── tools.py                 # MCP tool implementations
│       ├── schemas.py               # Pydantic schemas for chat
│       ├── routes.py                # FastAPI chat routes
│       └── session.py               # Conversation session management
├── mcp/
│   ├── __init__.py                  # Existing MCP server
│   ├── server.py                    # MCP server configuration
│   └── tools/
│       ├── add_task.py              # MCP add_task tool
│       ├── list_tasks.py            # MCP list_tasks tool
│       ├── complete_task.py         # MCP complete_task tool
│       ├── delete_task.py           # MCP delete_task tool
│       └── update_task.py           # MCP update_task tool
├── core/
│   ├── config.py                    # Environment config (existing + COHERE_API_KEY)
│   ├── security.py                  # JWT validation (existing)
│   └── dependencies.py              # Auth/DB dependencies (existing)
├── models/
│   ├── task.py                      # Task model (existing)
│   ├── conversation.py              # NEW: Conversation entity
│   └── message.py                   # NEW: Message entity
├── schemas/
│   ├── task.py                      # Task schemas (existing)
│   ├── chat.py                      # NEW: Chat request/response schemas
│   └── conversation.py              # NEW: Conversation/message schemas
└── db/
    ├── session.py                   # DB session (existing)
    └── init.py                      # DB initialization (existing + new tables)

frontend/
├── src/
│   ├── components/
│   │   └── Chatbot/                 # NEW: Chatbot components
│   │       ├── ChatbotButton.tsx    # Floating chat button
│   │       ├── ChatbotWindow.tsx    # Chat window panel
│   │       ├── ChatMessage.tsx      # Individual message component
│   │       ├── ChatInput.tsx        # Message input box
│   │       └── useChatbot.ts        # Chat hook (state, API calls)
│   ├── app/                         # Next.js app router
│   │   └── (main)/
│   │       └── layout.tsx           # Main layout (add ChatbotButton)
│   ├── services/
│   │   └── chatbot.ts               # API client for chat endpoints
│   └── types/
│       └── chatbot.ts               # TypeScript types for chat
└── .env.local                       # Environment variables (NEXT_PUBLIC_CHAT_API_URL)
```

**Structure Decision**: The project uses a modular architecture with clear separation:
- Backend: FastAPI with dedicated chatbot module under `app/chatbot/`
- MCP Tools: Separate directory under `mcp/tools/` for tool-based architecture
- Frontend: Next.js components under `src/components/Chatbot/` following existing patterns
- Database: New Conversation and Message models integrated with existing SQLModel structure

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| OpenAI Agents SDK with Cohere adapter | Required by specification for agent orchestration with Cohere LLM | Direct Cohere API calls would lack agent orchestration, tool selection, and conversation management capabilities |
| MCP server for tools | Constitution mandates AI tools execute only through MCP | Direct API calls from agent would violate constitution principle IV |
| Conversation persistence in database | Constitution mandates stateless backend with DB-backed state | In-memory sessions would violate constitution principle II |

## Implementation Plan

### Phase 0: Research & Discovery

1. **Cohere API Integration Patterns**
   - Research Cohere Chat API (command-r-plus, command-r models)
   - Understand message format, tool calling capabilities, streaming options
   - Identify adapter pattern for OpenAI Agents SDK compatibility

2. **OpenAI Agents SDK Architecture**
   - Study Agent, Runner, Context, and Tools structure
   - Understand tool calling mechanism and response parsing
   - Research stateless execution patterns

3. **MCP Server Best Practices**
   - Review MCP protocol specification
   - Study tool definition patterns and error handling
   - Understand tool security and user isolation enforcement

4. **Conversation Persistence Patterns**
   - Research database schema for conversation/message storage
   - Study session management in stateless architectures
   - Understand conversation continuity across requests

5. **JWT Authentication for Chat Endpoints**
   - Review Better Auth JWT integration patterns
   - Understand token validation in FastAPI dependencies
   - Research user isolation enforcement in MCP tools

### Phase 1: Design & Contracts

1. **Data Model Design**
   - Define Conversation entity (id, user_id, created_at, updated_at)
   - Define Message entity (id, conversation_id, user_id, role, content, created_at)
   - Establish relationships with existing Task and User entities
   - Define validation rules and indexes

2. **API Contracts**
   - Design POST /api/chatbot/message endpoint
   - Define request schema: { message, user_id, project_id, conversation_id? }
   - Define response schema: { reply, conversation_id, tool_calls? }
   - Create OpenAPI specification for chat endpoints
   - Define MCP tool contracts (add_task, list_tasks, complete_task, delete_task, update_task)

3. **Cohere Adapter Design**
   - Define CohereAgentModel interface
   - Specify send_message, parse_response, tool_call_detection methods
   - Design message format translation (Agent ↔ Cohere)

4. **Quickstart Guide**
   - Document environment variables (COHERE_API_KEY, JWT_SECRET, DATABASE_URL)
   - Provide local development setup instructions
   - Include testing procedures

### Phase 2: Implementation (via /sp.tasks)

1. **Backend Implementation**
   - Create chatbot module structure
   - Implement Cohere adapter
   - Build OpenAI Agents SDK agent
   - Develop MCP tools for task operations
   - Create FastAPI chat routes
   - Implement conversation persistence

2. **Frontend Implementation**
   - Build ChatbotButton component
   - Create ChatbotWindow component
   - Implement ChatMessage component
   - Develop useChatbot hook
   - Integrate with existing Todo UI

3. **Integration & Testing**
   - Connect frontend to backend
   - Test end-to-end chat flows
   - Validate MCP tool execution
   - Verify user isolation
   - Performance testing

### Phase 3: Deployment & Validation

1. **Security Validation**
   - Verify JWT authentication on all endpoints
   - Test user isolation enforcement
   - Validate prompt injection prevention

2. **Performance Testing**
   - Measure response times (p95 < 5s)
   - Test concurrent user handling (100 users)
   - Validate conversation history loading (< 2s)

3. **User Acceptance Testing**
   - Test all 5 core operations (create, list, complete, delete, update)
   - Validate conversation continuity
   - Verify error handling and user feedback

## Success Metrics Alignment

- **SC-001**: Task creation via chatbot < 10s → Backend responds < 2s, frontend displays immediately
- **SC-002**: Task list retrieval < 3s → MCP list_tasks optimized with database indexes
- **SC-003**: 95% success rate → Robust error handling and validation
- **SC-006**: JWT authentication enforced → Security middleware on all endpoints
- **SC-007**: Zero cross-user access → MCP tools enforce user_id verification
- **SC-008**: UI reflects changes < 1s → Frontend refreshes after tool execution
- **SC-009**: 100 concurrent users → Async operations, connection pooling, efficient queries
