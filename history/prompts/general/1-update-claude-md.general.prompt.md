---
id: 1
title: Update CLAUDE MD with Project Requirements
stage: general
date_iso: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: Update CLAUDE.md file with project requirements
labels: ["documentation", "setup", "requirements"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

# Update CLAUDE MD with Project Requirements

## Files Modified
 - D:\Q4-Hackathon2\H2-Phase-II\CLAUDE.md

## Prompt Text
Update the claude.md file based on my project requirements. In this file:

Use Auth Agent for authentication
Use Frontend Agent for frontend development (e.g., Next.js)
Use DB Agent for database design and operations
Use Backend Agent for FastAPI development
Below are my project requirements:

Basic Level Functionality
Objective: Using Claude Code and Spec-Kit Plus transform the console app into a modern multi-user web application with persistent storage.
💡Development Approach: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.
Requirements
Implement all 5 Basic Level features as a web application
Create RESTful API endpoints
Build responsive frontend interface
Store data in Neon Serverless PostgreSQL database
Authentication – Implement user signup/signin using Better Auth
Technology Stack
Layer
Technology
Frontend
Next.js 16+ (App Router)
Backend
Python FastAPI
ORM
SQLModel
Database
Neon Serverless PostgreSQL
Spec-Driven
Claude Code + Spec-Kit Plus
Authentication
Better Auth

Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.
How It Works
User logs in on Frontend → Better Auth creates a session and issues a JWT token
Frontend makes API call → Includes the JWT token in the Authorization: Bearer <token> header
Backend receives request → Extracts token from header, verifies signature using shared secret
Backend identifies user → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
Backend filters data → Returns only tasks belonging to that user

## Response Text
Updated the CLAUDE.md file to reflect the project requirements, including:
- Updated the primary goal to focus on transforming console applications to web applications
- Added information about using specialized agents (Auth, Frontend, DB, Backend)
- Included details about the technology stack (Next.js, FastAPI, SQLModel, Neon DB, Better Auth)
- Added authentication flow details with JWT tokens
- Updated Architect Guidelines to consider the specific tech stack
- Added Agentic Dev Stack workflow instructions
- Added project requirements section
- Updated project structure to include technology-specific directories
- Added technology-specific code standards

## Outcome
The CLAUDE.md file has been successfully updated to reflect the specific project requirements, technology stack, and development approach for transforming a console application into a modern multi-user web application with authentication, persistent storage, and responsive UI.