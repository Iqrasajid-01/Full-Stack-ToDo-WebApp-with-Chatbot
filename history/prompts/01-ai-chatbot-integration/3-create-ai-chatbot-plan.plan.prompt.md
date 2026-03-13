---
id: 2
title: create-ai-chatbot-plan
stage: plan
date: 2026-02-17
surface: agent
model: qwen-coder
feature: 2-ai-chatbot-integration
branch: 2-ai-chatbot-integration
user: dell
command: /sp.plan
labels: ["planning", "chatbot", "ai-integration", "architecture"]
links:
  spec: specs/01-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/01-ai-chatbot-integration/plan.md
 - specs/01-ai-chatbot-integration/research.md
 - specs/01-ai-chatbot-integration/data-model.md
 - specs/01-ai-chatbot-integration/contracts/chat-api.yaml
 - specs/01-ai-chatbot-integration/contracts/mcp-tools.yaml
 - specs/01-ai-chatbot-integration/quickstart.md
 - QWEN.md
tests:
 - None
---

## Prompt

/sp.plan /sp.specify

Project: AI-Native Todo SaaS Chatbot using OpenAI Agents SDK with Cohere LLM Integration

Constitution:
Follow the existing sp.constitution strictly. This chatbot must integrate into the existing AI-Native Todo SaaS architecture built using Next.js frontend, FastAPI backend, and Neon PostgreSQL database.

Objective:
Build a production-grade AI chatbot system integrated into the Todo SaaS that allows users to interact conversationally with their tasks. The chatbot must use OpenAI Agents SDK architecture but replace Gemini/OpenAI LLM with Cohere model as the reasoning engine.

The chatbot must support:

Core Functional Capabilities:
1. Add tasks via natural language
2. List tasks
3. Complete tasks
4. Delete tasks
5. Update tasks
6. Answer productivity questions
7. Provide summaries of tasks
8. Assist users conversationally

Architecture Requirements:

LLM Layer:
- Use Cohere as the LLM provider
- Use Cohere Chat API (command-r-plus or command-r model)
- Implement a Cohere adapter compatible with Agents SDK
- The adapter must translate Agent messages → Cohere format → Agent response format

Agent System:
- Use OpenAI Agents SDK architecture
- Implement Agent, Runner, Context, and Tools structure
- Context must include:
  - user_id
  - project_id
  - tasks list (loaded dynamically from database)
  - session state

Tools Layer:
Implement production-safe tools:

1. add_task_tool
2. list_tasks_tool
3. complete_task_tool
4. delete_task_tool
5. update_task_tool

Each tool must:
- Call FastAPI backend endpoints
- NOT directly manipulate database
- Use async HTTP calls
- Handle errors safely
- Return structured responses

Backend Integration (FastAPI):

Create chatbot module:

backend/
  app/
    chatbot/
      agent.py
      cohere_adapter.py
      tools.py
      schemas.py
      routes.py

routes.py must expose:

POST /api/chatbot/message

Request:
{
  "message": "string",
  "user_id": "string",
  "project_id": "string"
}

Response:
{
  "reply": "string"
}

Agent Flow:

User → FastAPI route → Agent Runner → Cohere → Tool if needed → Cohere → Response → Frontend

Frontend Integration (Next.js):

Requirements:

Chatbot UI must include:

1. Floating chatbot icon bottom-right
2. Click opens chat window
3. Chat window contains:
   - Message history
   - Input box
   - Send button
   - Loading indicator
4. Messages must persist during session
5. Calls FastAPI endpoint

Frontend structure:

components/
  Chatbot/
    ChatbotButton.tsx
    ChatbotWindow.tsx
    ChatMessage.tsx
    useChatbot.ts

UI behavior:

ChatbotButton:
- Floating circular button
- Fixed bottom-right
- Opens chatbot window

ChatbotWindow:
- Modal or expandable panel
- Scrollable messages
- Input form

useChatbot hook:
- Sends messages to backend
- Stores state
- Handles loading and errors

Database Integration:

Agent tools must call existing FastAPI Todo endpoints which interact with Neon PostgreSQL.

DO NOT access database directly from Agent.

Security Requirements:

- Validate user_id
- Validate project_id
- Prevent tool misuse
- Prevent prompt injection
- Restrict tool execution scope

Cohere Adapter Requirements:

Create abstraction layer:

class CohereAgentModel:

Functions:
- send_message(messages, context)
- parse_response()
- tool_call_detection()

Must support:
- multi-turn conversations
- tool calling
- structured responses

Session Management:

Chat session must:

- Maintain context
- Maintain conversation history
- Maintain tool results

Performance Requirements:

- Async everywhere
- No blocking calls
- Fast response time
- Production ready structure

Error Handling:

Must handle:

- Cohere API errors
- Network failures
- Invalid tool calls
- Backend failures

Logging:

Add logging for:

- Incoming messages
- Tool calls
- Cohere responses
- Errors

Testing Requirements:

Create test scenarios:

- Add task via chatbot
- List tasks via chatbot
- Complete task via chatbot
- Multi-step conversations
- Error scenarios

Deliverables:

1. Cohere adapter implementation
2. Agent implementation
3. Tool implementations
4. FastAPI routes
5. Frontend chatbot components
6. Integration layer
7. Fully working chatbot end-to-end

Acceptance Criteria:

Chatbot must successfully:

- Receive message from frontend
- Process via Cohere
- Call tools when needed
- Return correct response
- Update Todo system correctly

Non-goals:

- Do not use Gemini
- Do not use OpenAI LLM
- Only use Cohere

Quality Requirements:

- Clean architecture
- Modular code
- Production-ready structure
- Fully typed code
- No placeholder logic

Output Format:

Provide:

1. System architecture explanation
2. File structure
3. Backend implementation
4. Cohere adapter code
5. Agent code
6. Tools code
7. FastAPI routes
8. Frontend components
9. Integration instructions
10. Testing instructions

Execution Mode:

STRICT production implementation mode.
No pseudo code.
No placeholders.
Full working code only.

## Response snapshot

Created comprehensive implementation plan for AI chatbot integration with all Phase 0 and Phase 1 deliverables:

**Phase 0 (Research)**:
- research.md with Cohere API integration patterns, OpenAI Agents SDK architecture, MCP server best practices, conversation persistence patterns, JWT authentication flow, error handling patterns, and performance optimization strategies

**Phase 1 (Design & Contracts)**:
- data-model.md: Conversation and Message entity definitions with SQLModel schemas, database migrations, query patterns, and security considerations
- contracts/chat-api.yaml: OpenAPI specification for chatbot REST endpoints
- contracts/mcp-tools.yaml: MCP tool contracts for add_task, list_tasks, complete_task, delete_task, update_task
- quickstart.md: Complete setup and testing guide
- QWEN.md: Updated agent context with new technology stack

## Outcome

- ✅ Impact: Complete implementation plan created with architecture, data models, API contracts, and development guidelines for AI chatbot integration
- 🧪 Tests: All constitution checks passed, no violations detected
- 📁 Files: Created 7 planning artifacts in specs/01-ai-chatbot-integration/ plus QWEN.md agent context
- 🔁 Next prompts: Ready for /sp.tasks to break implementation into actionable tasks
- 🧠 Reflection: Plan maintains constitution compliance (stateless backend, user isolation, MCP tools only, Cohere LLM)

## Evaluation notes (flywheel)

- Failure modes observed: None - all gates passed
- Graders run and results (PASS/FAIL): PASS - Constitution check cleared, all phases complete
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.tasks for task breakdown
