---
name: backend-skill
description: Generate backend routes, handle requests/responses, and connect to the database. Use for FastAPI backend development.
---

# Backend Skill Design

## Instructions

1. **API Routes**
   - Implement RESTful endpoints for Task CRUD operations
   - Organize routes logically under `/api/`
   - Include route validation and proper HTTP status codes

2. **Request & Response Handling**
   - Parse incoming JSON or form data
   - Validate inputs and enforce constraints
   - Return structured JSON responses
   - Handle errors using proper HTTP exceptions

3. **Database Integration**
   - Connect to Neon PostgreSQL via SQLModel
   - Ensure each task is associated with the authenticated user
   - Implement query filtering based on user identity
   - Perform create, read, update, delete operations securely

## Best Practices
- Keep route handlers clear and readable
- Reuse logic via helper functions where possible
- Enforce JWT authentication on all endpoints
- Avoid hardcoding credentials or secrets
- Write code that is testable and maintainable

Use this skill whenever a backend API endpoint or database interaction is needed.
