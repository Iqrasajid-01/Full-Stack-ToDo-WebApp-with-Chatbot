---
id: 1
title: "Update constitution for AI chatbot integration"
stage: constitution
date: 2026-02-17
surface: agent
model: Claude Sonnet 4.5
feature: ai-chatbot-integration
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "ai-integration", "mcp", "cohere"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests: []
---

# Prompt History Record: Update constitution for AI chatbot integration

## PROMPT_TEXT

/sp.constitution

Project: AI-Powered Todo Chatbot Integration (Phase III) — Cohere + Agents SDK + MCP

Objective:
Integrate an AI-powered conversational chatbot into the existing full-stack Todo SaaS application. The chatbot must enable users to manage their tasks using natural language and perform full task lifecycle operations (create, read, update, complete, delete) securely and reliably.

The chatbot must be integrated into the existing architecture:

Frontend: Next.js (ChatKit-based UI)
Backend: FastAPI
Database: Neon Serverless PostgreSQL
Authentication: Better Auth with JWT
AI Provider: Cohere API
AI Framework: OpenAI Agents SDK
Tool Interface: MCP (Model Context Protocol) Server

This chatbot must operate as an intelligent control layer over the existing Todo system.


--------------------------------------------------
CORE PRINCIPLES
--------------------------------------------------

1. Spec-Driven Development Only
- All chatbot features must be implemented strictly through Spec-Kit Plus workflow.
- No manual coding outside spec-driven agent execution.
- Every feature must originate from specification → plan → tasks → implementation.

2. Stateless Backend Architecture
- FastAPI backend must remain stateless.
- All chat state must be persisted in Neon PostgreSQL database.
- Backend must not store conversation state in memory.

3. Secure Multi-User Isolation
- Each user must only access their own tasks.
- All MCP tool calls must enforce authenticated user ID verification.
- JWT tokens issued by Better Auth must be validated on every request.

4. AI Tool-Based Execution Only
- AI agent must never directly modify database.
- All task operations must occur exclusively through MCP tools.
- MCP tools serve as the only interface between AI and database.

5. Cohere API as LLM Provider
- Cohere API must be used as the primary language model provider.
- Cohere API key must be stored securely in environment variable:

  COHERE_API_KEY

- API keys must never be exposed in frontend code or logs.


--------------------------------------------------
SYSTEM ARCHITECTURE RULES
--------------------------------------------------

Required architecture layers:

Frontend Layer:
- Next.js ChatKit UI
- Handles chat interaction
- Sends user messages to FastAPI backend
- Displays AI responses

Backend Layer:
- FastAPI REST server
- Provides /api/{user_id}/chat endpoint
- Verifies JWT authentication
- Loads conversation history
- Executes AI agent
- Calls MCP tools

AI Layer:
- OpenAI Agents SDK
- Configured to use Cohere API
- Responsible for reasoning and tool selection
- Converts natural language into MCP tool calls

Tool Layer:
- MCP server exposes standardized tools:

  add_task
  list_tasks
  update_task
  complete_task
  delete_task

Database Layer:
- Neon PostgreSQL
- Stores:

  users
  tasks
  conversations
  messages


--------------------------------------------------
DATA PERSISTENCE STANDARDS
--------------------------------------------------

Conversation persistence is mandatory.

Database must store:

Conversations table:
- id
- user_id
- created_at
- updated_at

Messages table:
- id
- conversation_id
- user_id
- role (user or assistant)
- content
- created_at

Tasks table:
- id
- user_id
- title
- description
- completed
- created_at
- updated_at


--------------------------------------------------
AI AGENT BEHAVIOR RULES
--------------------------------------------------

The AI agent must:

- Interpret natural language commands
- Select appropriate MCP tools
- Execute correct tool calls
- Confirm actions to user
- Handle errors gracefully
- Maintain conversation continuity via database history

The AI must support:

Task creation
Task listing
Task completion
Task deletion
Task updating
Task status queries
User task summaries


--------------------------------------------------
SECURITY REQUIREMENTS
--------------------------------------------------

Mandatory protections:

- JWT verification on every request
- User ID validation before tool execution
- Strict user data isolation
- No cross-user data access allowed
- Secure storage of environment variables

Environment variables required:

COHERE_API_KEY = kYoTdJFeEPVLge2BOUB7J6F9sn9oKkbMjq97fFGr
DATABASE_URL
BETTER_AUTH_SECRET


--------------------------------------------------
CODE QUALITY STANDARDS
--------------------------------------------------

All generated code must be:

Production-grade
Modular and maintainable
Fully typed where applicable
Properly structured
Error-handled
Secure by default

Backend must follow FastAPI best practices.

Frontend must follow Next.js App Router best practices.


--------------------------------------------------
SPEC-KIT MONOREPO RULES
--------------------------------------------------

Project must follow Spec-Kit structure:

/specs
/specs/features
/specs/api
/specs/database
/specs/ui

/frontend
/backend


All implementations must reference specs.


--------------------------------------------------
SUCCESS CRITERIA
--------------------------------------------------

Chatbot is considered complete only if:

Users can add tasks via chat
Users can list tasks via chat
Users can complete tasks via chat
Users can update tasks via chat
Users can delete tasks via chat

Conversation history persists after restart
System works with multiple users securely
AI correctly uses MCP tools
Cohere API powers all AI responses

System must function as a fully integrated AI control interface for the Todo SaaS.


--------------------------------------------------
NON-GOALS
--------------------------------------------------

The chatbot must NOT:

Directly modify database without MCP tools
Store secrets in frontend
Access unauthorized user data
Operate without authentication


--------------------------------------------------
FINAL GOVERNING RULE
--------------------------------------------------

All future specifications, plans, and implementations must strictly follow this constitution.

This constitution governs all chatbot development decisions.

## RESPONSE_TEXT

Updated the project constitution to reflect the AI-Powered Todo Chatbot Integration project. The new constitution includes:

1. Core Principles aligned with AI integration requirements
2. Updated Technology Standards reflecting the new architecture
3. Expanded Agents & Responsibilities including new AI-focused roles
4. Governance rules for the new AI integration project

The constitution version was updated from 1.1.0 to 2.0.0 to reflect the major changes in project scope and architecture.