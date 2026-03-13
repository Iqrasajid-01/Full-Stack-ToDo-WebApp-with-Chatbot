---
id: 1
title: Amend Constitution
stage: constitution
date: 2026-02-06
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: Claude Code
command: /sp.constitution
labels: [constitution, governance, principles]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .specify/templates/plan-template.md
  - .specify/templates/tasks-template.md
tests:
  - none
---

## Prompt

/sp.constitution

Project: Phase II – Full-Stack Todo Web Application (Spec-Driven, Agentic)

Purpose:
Transform the Phase I console-based todo application into a secure, modern, multi-user
full-stack web application using a strictly spec-driven and agentic development workflow.

All implementation must be performed via agents and skills using Claude Code and Spec-Kit Plus.
No manual coding is allowed.

────────────────────────────────────────────
CORE PRINCIPLES
────────────────────────────────────────────

1. Spec-Driven Authority
- The /specs directory is the single source of truth.
- No feature, API, UI, or database change is allowed without a corresponding spec.
- Agents must always read and reference relevant specs before acting.

2. Agentic Separation of Responsibility
- Each agent operates strictly within its defined role.
- Agents may only use explicitly assigned skills.
- No agent may perform work outside its responsibility domain.

3. Professional Full-Stack Quality
- UI must be modern, responsive, accessible, and visually polished.
- Backend must be secure, scalable, and maintainable.
- Database must be normalized, indexed, and migration-safe.

4. Security First
- Authentication is mandatory for all API requests.
- JWT-based auth is enforced end-to-end.
- User data isolation is non-negotiable.

5. Reproducibility & Traceability
- All decisions must be traceable through specs or ADRs.
- Architecture decisions must be documented.
- Codebase must be deterministic and reviewable.

────────────────────────────────────────────
TECHNOLOGY STANDARDS
────────────────────────────────────────────

Frontend:
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Centralized API client
- Responsive AI-ready components

Backend:
- Python FastAPI
- SQLModel ORM
- RESTful API architecture
- JWT verification middleware

Database:
- Neon Serverless PostgreSQL
- SQLModel-managed schemas
- Indexed, relational, migration-safe design

Authentication:
- BetterAuth (Frontend)
- JWT tokens for backend verification
- Shared JWT secret via environment variables

Spec System:
- Spec-Kit Plus
- Claude Code
- Structured specs in /specs directory

────────────────────────────────────────────
AGENTS & RESPONSIBILITIES
────────────────────────────────────────────

spec-writer
- Writes and updates all feature, API, database, and UI specifications.
- Defines acceptance criteria and edge cases.

senior-arch-planner
- Defines system architecture and data flow.
- Plans frontend-backend-auth-database interactions.

schema-model-writer
- Designs SQLModel schemas and relationships.
- Ensures indexes, constraints, and migrations.

backend-manager
- Implements FastAPI app structure and business logic.
- Manages REST endpoints and database operations.

auth-manager
- Designs authentication flow using BetterAuth and JWT.
- Coordinates frontend-backend auth integration.

auth-checker
- Verifies JWT validation logic and access control.
- Ensures user isolation and 401 handling.

frontend-security-guardian
- Ensures frontend token safety and secure API usage.
- Handles auth edge cases (expiry, logout).

adr-tracker-backend
- Records backend architecture decisions.
- Maintains technical reasoning for implementation choices.

adr-decision-tracker
- Records high-level architectural and product decisions.
- Ensures traceability for hackathon evaluation.

────────────────────────────────────────────
SKILLS & USAGE CONSTRAINTS
────────────────────────────────────────────

monorepo-bootstrap
- Initializes Spec-Kit compatible monorepo.
- Sets CLAUDE.md context layering.

database-skill
- Creates tables, relations, and migrations.
- Enforces schema integrity.

neon-db-connection
- Configures Neon PostgreSQL connectivity.
- Manages environment-based configuration.

backend-skill
- Implements FastAPI routes and logic.
- Handles ORM operations and errors.

jwt-auth-middleware
- Verifies JWT tokens in FastAPI.
- Extracts and validates user identity.

betterauth-jwt-setup
- Enables JWT issuance in BetterAuth.
- Configures expiry and secrets.

auth-skill
- Handles signup, signin, and session logic.
- Coordinates auth lifecycle.

centralized-api-client
- Manages all frontend API communication.
- Auto-attaches JWT tokens to requests.

frontend-pages-components
- Builds Next.js pages and UI components.
- Implements task CRUD UI.

responsive-ai-components
- Ensures responsive, accessi

## Response snapshot

Updated the project constitution by replacing the template placeholders with concrete values based on the user input. Created a new constitution with the following core principles:

1. Spec-Driven Authority
2. Agentic Separation of Responsibility
3. Professional Full-Stack Quality
4. Security First
5. Reproducibility & Traceability
6. Agentic Dev Stack Workflow

Also updated supporting sections for Technology Standards, Agents & Responsibilities, and Governance. Updated the plan and tasks templates to align with the new constitution principles.

## Outcome

- ✅ Impact: New constitution established with 6 core principles and supporting sections
- 🧪 Tests: No tests run for this change
- 📁 Files: Updated .specify/memory/constitution.md, .specify/templates/plan-template.md, .specify/templates/tasks-template.md
- 🔁 Next prompts: Ready for spec-driven development workflow
- 🧠 Reflection: Constitution now reflects the agentic development approach with proper separation of responsibilities

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin with /sp.spec to create feature specification