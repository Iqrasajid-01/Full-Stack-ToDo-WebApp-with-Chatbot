# Feature Specification: Backend – Phase II Todo Web Application

**Feature Branch**: `001-backend-todo-app`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "# /sp.specify
# Backend – Phase II Todo Web Application

## Objective
Build a **secure, scalable, and professional backend service** for a multi-user Todo web application.
The backend must expose RESTful APIs, enforce user-level data isolation, and persist data reliably.

---

## Backend Responsibilities
- Handle all business logic
- Enforce authentication and authorization
- Manage database interactions
- Validate requests and responses
- Serve as the single source of truth for task data

---

## Technology Stack
- Framework: FastAPI (Python)
- ORM: SQLModel
- Database: PostgreSQL (Neon Serverless)
- Authentication: JWT-based authentication
- Data validation: Pydantic models

---

## API Design Rules
- All routes must be prefixed with `/api`
- RESTful conventions must be followed strictly
- HTTP methods must reflect intent
- JSON must be used for all request and response bodies

---

## Authentication & Authorization

### Authentication
- All API endpoints must require a valid JWT token
- JWT must be read from the `Authorization` header:
  `Authorization: Bearer <token>`
- Token validity and expiration must be verified

### Authorization
- User identity must be derived from the JWT
- Every request must be scoped to the authenticated user
- Cross-user access must be blocked at all times

---

## Task Management Logic

### Core Operations
Authenticated users must be able to:
- Create tasks
- Retrieve all their tasks
- Retrieve a single task
- Update a task
- Delete a task
- Toggle task completion status

### Task Ownership
- Each task must belong to exactly one user
- Ownership must be verified before any update or delete

---

## API Endpoints

| Method | Endpoint | Description |
|------|---------------------------------------|------------------------------|
| GET | `/api/tasks` | List user tasks |
| POST | `/api/tasks` | Create a new task |
| GET | `/api/tasks/{task_id}` | Get task details |
| PUT | `/api/tasks/{task_id}` | Update a task |
| DELETE | `/api/tasks/{task_id}` | Delete a task |
| PATCH | `/api/tasks/{task_id}/complete` | Toggle completion status |

---

## Data Model Rules

### Task Entity
- id: integer (primary key)
- user_id: string (foreign key)
- title: string (required)
- description: string (optional)
- completed: boolean (default false)
- created_at: timestamp
- updated_at: timestamp

---

## Database Rules
- Use SQLModel for all database interactions
- Enforce foreign key constraints
- Use indexes for `user_id` and `completed` fields
- Database connection must be configurable via environment variables

---

## Validation Rules
- Task title must not be empty
- Input data must be validated before persistence
- Invalid input must return appropriate errors

---

## Error Handling
- 400 → Invalid input
- 401 → Unauthorized (missing/invalid token)
- 403 → Forbidden (cross-user access)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated User Manages Tasks (Priority: P1)

An authenticated user can perform all CRUD operations on their own tasks, ensuring data isolation and proper authorization.

**Why this priority**: This is the core functionality of the Todo application, enabling users to manage their personal tasks securely. Without this, the application provides no value.

**Independent Test**: Can be fully tested by creating a user, logging in, and then performing all task management operations (create, retrieve all, retrieve single, update, delete, toggle completion) for only that user. This delivers the core task management value.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they create a new task with a title and optional description, **Then** the task is successfully created and associated with their user ID.
2. **Given** an authenticated user with existing tasks, **When** they request to retrieve all their tasks, **Then** a list of only their tasks is returned.
3. **Given** an authenticated user with a specific task, **When** they request to retrieve that task by ID, **Then** the details of that task are returned.
4. **Given** an authenticated user with a specific task, **When** they update the title or description of that task, **Then** the task's details are updated successfully.
5. **Given** an authenticated user with a specific task, **When** they delete that task by ID, **Then** the task is removed from their list of tasks.
6. **Given** an authenticated user with a specific task, **When** they toggle the completion status of that task, **Then** the task's completion status is updated.
7. **Given** an authenticated user, **When** they attempt to access or modify a task belonging to another user, **Then** a 403 Forbidden error is returned, and the operation is denied.
8. **Given** an unauthenticated user, **When** they attempt to access any API endpoint, **Then** a 401 Unauthorized error is returned.

---

### User Story 2 - Task Input Validation (Priority: P2)

The backend service validates task input to ensure data integrity and provides clear error messages for invalid input.

**Why this priority**: Ensures the quality and consistency of data stored in the database, preventing malformed tasks and improving user experience with helpful error feedback.

**Independent Test**: Can be fully tested by attempting to create or update tasks with invalid data (e.g., empty title, incorrect data types) and verifying that appropriate 400 Bad Request errors are returned.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they attempt to create a task with an empty title, **Then** a 400 Bad Request error is returned with a descriptive message.
2. **Given** an authenticated user, **When** they attempt to update a task with an empty title, **Then** a 400 Bad Request error is returned with a descriptive message.

---

### Edge Cases

- What happens when an authenticated user tries to access a task ID that does not exist?
  - The API should return a 404 Not Found error.
- How does the system handle concurrent updates to the same task?
  - The system should ensure data consistency, potentially through optimistic locking or last-write-wins depending on the chosen ORM/database features. (Assumed last-write-wins by default for simplicity unless specific requirements dictate otherwise).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The backend service MUST expose RESTful API endpoints for task management.
- **FR-002**: All API endpoints MUST require a valid JWT token for authentication.
- **FR-003**: The backend MUST verify JWT token validity and expiration.
- **FR-004**: The backend MUST derive user identity from the JWT token.
- **FR-005**: Every API request MUST be scoped to the authenticated user, preventing cross-user access.
- **FR-006**: Authenticated users MUST be able to create tasks with a title (required) and an optional description.
- **FR-007**: Authenticated users MUST be able to retrieve all their tasks.
- **FR-008**: Authenticated users MUST be able to retrieve a single task by its ID.
- **FR-009**: Authenticated users MUST be able to update a task by its ID.
- **FR-010**: Authenticated users MUST be able to delete a task by its ID.
- **FR-011**: Authenticated users MUST be able to toggle a task's completion status.
- **FR-012**: Each task MUST belong to exactly one user.
- **FR-013**: The backend MUST verify task ownership before allowing any update or delete operation.
- **FR-014**: The backend MUST use SQLModel for all database interactions.
- **FR-015**: The backend MUST enforce foreign key constraints for `user_id`.
- **FR-016**: The backend MUST use indexes for `user_id` and `completed` fields in the database.
- **FR-017**: The database connection MUST be configurable via environment variables.
- **FR-018**: Task titles MUST NOT be empty.
- **FR-019**: All input data MUST be validated before persistence.
- **FR-020**: Invalid input MUST return appropriate HTTP 400 (Bad Request) errors.
- **FR-021**: Missing or invalid JWT tokens MUST return HTTP 401 (Unauthorized) errors.
- **FR-022**: Attempts at cross-user access MUST return HTTP 403 (Forbidden) errors.
- **FR-023**: API routes MUST be prefixed with `/api`.
- **FR-024**: HTTP methods MUST reflect RESTful intent.
- **FR-025**: JSON MUST be used for all request and response bodies.

### Key Entities *(include if feature involves data)*

- **Task**: Represents a single todo item. Key attributes include `id`, `user_id`, `title`, `description`, `completed`, `created_at`, and `updated_at`.
- **User**: Represents an authenticated user of the application. Tasks are associated with a user via `user_id`. (Assumed user entity handled by authentication system, only `user_id` reference needed for tasks).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authenticated users can successfully perform all CRUD operations on their tasks within 500ms (p95 latency).
- **SC-002**: The backend service can handle 100 concurrent authenticated users managing tasks without degradation in performance (latency increase > 10%).
- **SC-003**: 100% of invalid input attempts are met with appropriate 400 Bad Request errors.
- **SC-004**: 100% of unauthorized access attempts (missing/invalid JWT) are met with 401 Unauthorized errors.
- **SC-005**: 100% of forbidden access attempts (cross-user task access) are met with 403 Forbidden errors.
- **SC-006**: The database schema correctly reflects the Task entity and its constraints, as verified by automated schema migration tests.
- **SC-007**: Task data is persistently stored and retrieved from the Neon Serverless PostgreSQL database with no data loss during normal operations.
- **SC-008**: All API endpoints conform to the `/api` prefix and RESTful conventions.
