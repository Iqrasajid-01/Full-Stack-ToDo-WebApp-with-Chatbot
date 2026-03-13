---
id: 1
title: create-ai-chatbot-spec
stage: spec
date: 2026-02-17
surface: agent
model: qwen-coder
feature: 2-ai-chatbot-integration
branch: 2-ai-chatbot-integration
user: dell
command: /sp.specify
labels: ["specification", "chatbot", "ai-integration"]
links:
  spec: specs/2-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/2-ai-chatbot-integration/spec.md
 - specs/2-ai-chatbot-integration/checklists/requirements.md
tests:
 - None
---

## Prompt

Project: AI Todo Chatbot Integration using Cohere API + OpenAI Agents SDK + MCP Server Objective: Integrate a production-grade AI chatbot into the existing full-stack Todo web application. The chatbot must allow authenticated users to manage their tasks using natural language through a ChatKit-based frontend interface. The chatbot must use: - Cohere API as the language model provider - OpenAI Agents SDK as the agent orchestration framework - MCP (Model Context Protocol) server to expose Todo task operations as tools - FastAPI backend for chat endpoint and agent execution - Neon PostgreSQL database for persistent storage - Better Auth with JWT for authentication - Next.js ChatKit frontend for the chat interface This chatbot must integrate directly into the existing Todo backend and database without creating a separate system. -------------------------------------------------- MODEL PROVIDER REQUIREMENTS -------------------------------------------------- The AI agent must use Cohere API as the model provider. The OpenAI Agents SDK must be configured to call Cohere models instead of Gemini or OpenAI models. Environment variable required: COHERE_API_KEY The agent must use Cohere for: - Natural language understanding - Tool selection - Response generation - Conversation continuity -------------------------------------------------- AGENT ARCHITECTURE REQUIREMENTS -------------------------------------------------- Implement an agent using OpenAI Agents SDK with: - Context model for user and conversation state - Tool-based architecture using MCP tools - Stateless execution model - Database-backed conversation persistence The agent must: - Interpret user natural language commands - Select appropriate MCP tools - Execute MCP tools - Generate confirmation responses - Handle errors gracefully - Maintain conversational continuity using stored messages -------------------------------------------------- MCP SERVER REQUIREMENTS -------------------------------------------------- Implement MCP server exposing the following tools: add_task list_tasks complete_task delete_task update_task Each MCP tool must: - Accept user_id parameter - Use SQLModel ORM - Connect to Neon PostgreSQL - Perform secure database operations - Return structured responses MCP tools must enforce strict user isolation. -------------------------------------------------- BACKEND CHAT ENDPOINT REQUIREMENTS -------------------------------------------------- Implement FastAPI endpoint: POST /api/{user_id}/chat Request body: conversation_id (optional) message (required) Backend must perform: 1. Verify JWT token using Better Auth secret 2. Verify authenticated user matches user_id 3. Load conversation history from database 4. Store user message in Message table 5. Execute OpenAI Agents SDK agent using Cohere API 6. Allow agent to call MCP tools 7. Store assistant response in database 8. Return response to frontend Response format: conversation_id response tool_calls -------------------------------------------------- DATABASE REQUIREMENTS -------------------------------------------------- Implement persistent chat storage. Conversation table: id user_id created_at updated_at Message table: id conversation_id user_id role content created_at These tables must integrate with existing Neon database. -------------------------------------------------- FRONTEND CHATKIT REQUIREMENTS -------------------------------------------------- Integrate ChatKit chat interface into existing Next.js frontend. Frontend must include: Chatbot icon button in UI Chat window panel Message input box Message display area Frontend must: Call FastAPI chat endpoint Send JWT token in Authorization header Maintain conversation_id Display assistant responses Display tool confirmation responses UI must be modern, responsive, and professional. -------------------------------------------------- INTEGRATION REQUIREMENTS -------------------------------------------------- Chatbot must integrate with existing Todo system. Agent must use MCP tools connected to the same database used by Todo REST API. All Todo operations performed via chatbot must immediately reflect in Todo UI. -------------------------------------------------- SECURITY REQUIREMENTS -------------------------------------------------- All chat requests must require valid JWT token. Backend must: Validate JWT signature Extract authenticated user ID Enforce user-level data isolation Users must never access other users' tasks. -------------------------------------------------- CONVERSATION FLOW REQUIREMENTS -------------------------------------------------- Each chat request must follow stateless execution: 1. Receive message 2. Load conversation history from database 3. Store user message 4. Execute agent with MCP tools using Cohere API 5. Store assistant response 6. Return response Backend must not store in-memory state. -------------------------------------------------- SUCCESS CRITERIA -------------------------------------------------- Chatbot is complete only if: Users can create tasks via chat Users can list tasks via chat Users can complete tasks via chat Users can delete tasks via chat Users can update tasks via chat Chatbot uses Cohere API successfully Agent correctly uses MCP tools ChatKit frontend works correctly Conversation history persists JWT authentication enforced Full integration with existing Todo backend -------------------------------------------------- NOT IN SCOPE -------------------------------------------------- Voice chatbot Manual task editing outside MCP tools Unauthenticated chatbot access -------------------------------------------------- OUTPUT REQUIREMENTS -------------------------------------------------- Claude must generate production-ready specifications under: /specs/features/chatbot.md /specs/api/chat-endpoint.md /specs/database/chat-schema.md /specs/tools/mcp-tools.md /specs/ui/chatkit-interface.md /specs/agent/cohere-agent.md

## Response snapshot

Created feature specification at `specs/2-ai-chatbot-integration/spec.md` with complete user scenarios, functional requirements, success criteria, and quality checklist. All specification quality validations passed.

## Outcome

- ✅ Impact: Feature specification created for AI chatbot integration with 5 user stories, 15 functional requirements, and 10 measurable success criteria
- 🧪 Tests: Specification quality checklist created and all items passed validation
- 📁 Files: Created spec.md and checklists/requirements.md in specs/2-ai-chatbot-integration/
- 🔁 Next prompts: Ready for /sp.clarify or /sp.plan phase
- 🧠 Reflection: Specification focuses on user value and business needs without implementation details

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All checklist items validated
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase with /sp.plan
