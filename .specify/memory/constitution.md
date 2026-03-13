<!--
Sync Impact Report:
Version change: 1.1.0 → 2.0.0
Modified principles: I, II, III, IV, V, VI (major updates to reflect AI chatbot integration)
Added sections: New Core Principles for AI integration
Removed sections: Previous principles reworked
Templates requiring updates:
  - ✅ .specify/templates/plan-template.md (updated Constitution Check section)
  - ✅ .specify/templates/spec-template.md (updated to reflect AI integration requirements)
  - ✅ .specify/templates/tasks-template.md (updated to reflect new AI integration tasks)
  - ⚠ Pending .specify/templates/commands/*.md (to be reviewed for consistency)
  - ⚠ Pending README.md or similar docs (to be reviewed for consistency)
Follow-up TODOs: None
-->

# AI-Powered Todo Chatbot Integration Constitution (Phase III) — Cohere + Agents SDK + MCP

## Core Principles

### I. Spec-Driven Development Only
All chatbot features must be implemented strictly through Spec-Kit Plus workflow. No manual coding outside spec-driven agent execution. Every feature must originate from specification → plan → tasks → implementation.

### II. Stateless Backend Architecture
FastAPI backend must remain stateless. All chat state must be persisted in Neon PostgreSQL database. Backend must not store conversation state in memory.

### III. Secure Multi-User Isolation
Each user must only access their own tasks. All MCP tool calls must enforce authenticated user ID verification. JWT tokens issued by Better Auth must be validated on every request.

### IV. AI Tool-Based Execution Only
AI agent must never directly modify database. All task operations must occur exclusively through MCP tools. MCP tools serve as the only interface between AI and database.

### V. Cohere API as LLM Provider
Cohere API must be used as the primary language model provider. Cohere API key must be stored securely in environment variable. API keys must never be exposed in frontend code or logs.

### VI. Agentic Dev Stack Workflow
Follow the Agentic Dev Stack workflow for all development: Write spec → Generate plan → Break into tasks → Implement via Claude Code.

## Technology Standards

Frontend: Next.js 16+ (ChatKit-based UI), TypeScript, Tailwind CSS, Centralized API client, Responsive AI-ready components. Backend: Python FastAPI, SQLModel ORM, RESTful API architecture, JWT verification middleware. Database: Neon Serverless PostgreSQL, SQLModel-managed schemas, Indexed, relational, migration-safe design. Authentication: BetterAuth (Frontend), JWT tokens for backend verification, Shared JWT secret via environment variables. AI Layer: Cohere API, OpenAI Agents SDK, MCP (Model Context Protocol) server. Tool Interface: Standardized MCP tools (add_task, list_tasks, update_task, complete_task, delete_task). Spec System: Spec-Kit Plus, Claude Code, Structured specs in /specs directory.

## Agents & Responsibilities

spec-writer: Writes and updates all feature, API, database, and UI specifications. Defines acceptance criteria and edge cases. senior-arch-planner: Defines system architecture and data flow. Plans frontend-backend-auth-database-AI interactions. schema-model-writer: Designs SQLModel schemas and relationships. Ensures indexes, constraints, and migrations. backend-manager: Implements FastAPI app structure and business logic. Manages REST endpoints and database operations. auth-manager: Designs authentication flow using BetterAuth and JWT. Coordinates frontend-backend auth integration. auth-checker: Verifies JWT validation logic and access control. Ensures user isolation and 401 handling. frontend-security-guardian: Ensures frontend token safety and secure API usage. Handles auth edge cases (expiry, logout). ai-agent-engineer: Implements AI agent logic using OpenAI Agents SDK. Connects MCP tools for intelligent task management. mcp-server-engineer: Builds MCP server infrastructure. Implements tools for task management accessible by AI agents. chatbot-architecture-planner: Designs chatbot system architecture. Plans MCP server structures and agent execution flows. chat-backend-engineer: Implements chat backend functionality. Manages conversation persistence and message storage. chat-frontend-engineer: Builds chatbot frontend interface. Connects ChatKit to backend API and manages message handling. chat-integration-tester: Tests end-to-end chatbot functionality. Validates MCP tools integration and agent responses. adr-tracker-backend: Records backend architecture decisions. Maintains technical reasoning for implementation choices. adr-decision-tracker: Records high-level architectural and product decisions. Ensures traceability for hackathon evaluation.

## Governance

All implementation must be performed via agents and skills using Claude Code and Spec-Kit Plus. No manual coding is allowed. All decisions must be traceable through specs or ADRs. Architecture decisions must be documented. The constitution supersedes all other practices. All AI integration features must follow the defined system architecture with proper layer separation between frontend, backend, AI, tools, and database.

**Version**: 2.0.0 | **Ratified**: 2026-02-17 | **Last Amended**: 2026-02-17