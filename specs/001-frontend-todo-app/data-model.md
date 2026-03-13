# Data Model: Frontend Web Application for Todo System

## User Entity

**Definition**: Represents a registered user with authentication status and associated tasks

**Fields**:
- `id`: Unique identifier for the user
- `email`: User's email address (primary login identifier)
- `name`: Optional display name for the user
- `createdAt`: Timestamp of account creation
- `updatedAt`: Timestamp of last account update
- `isActive`: Boolean indicating if the account is active

**Validations**:
- Email must be a valid email format
- Email must be unique across all users
- Required fields: id, email, createdAt

**State Transitions**:
- `pending` → `active` (after email verification)
- `active` → `suspended` (admin action)
- `suspended` → `active` (admin action)

## Task Entity

**Definition**: Represents an individual task with title, description, completion status, and timestamps

**Fields**:
- `id`: Unique identifier for the task
- `userId`: Foreign key linking to the owning user
- `title`: Short title or summary of the task
- `description`: Optional detailed description of the task
- `isCompleted`: Boolean indicating completion status
- `priority`: Enum of priority level (low, medium, high)
- `dueDate`: Optional deadline for task completion
- `createdAt`: Timestamp of task creation
- `updatedAt`: Timestamp of last task update
- `completedAt`: Optional timestamp when task was marked as completed

**Validations**:
- Title must not be empty
- UserId must reference an existing user
- Priority must be one of the allowed values
- Due date must be in the future if provided
- Required fields: id, userId, title, isCompleted, createdAt

**State Transitions**:
- `pending` → `completed` (when user marks task complete)
- `completed` → `pending` (when user unmarks task)

## Session Entity

**Definition**: Represents an active user session for authentication and authorization

**Fields**:
- `id`: Unique identifier for the session
- `userId`: Foreign key linking to the authenticated user
- `token`: JWT token value
- `expiresAt`: Timestamp when the token expires
- `createdAt`: Timestamp of session creation
- `lastAccessedAt`: Timestamp of last activity
- `deviceInfo`: Information about the device used for login
- `isActive`: Boolean indicating if the session is currently active

**Validations**:
- UserId must reference an existing user
- Token must be properly formatted JWT
- ExpiresAt must be in the future
- Required fields: id, userId, token, expiresAt, createdAt

**State Transitions**:
- `active` → `expired` (when token expires)
- `active` → `terminated` (when user logs out)
- `expired` → `refreshed` (when token is refreshed)

## Frontend-Specific Data Types

### UI State Models
- **TaskFilter**: Controls which tasks are displayed (all, pending, completed)
- **LoadingState**: Tracks loading status of various UI components
- **ErrorState**: Captures and displays various error conditions
- **FormState**: Manages form validation and submission states

### API Response Models
- **ApiResponse<T>**: Generic wrapper for API responses with status, data, and error information
- **PaginatedResponse<T>**: Handles paginated data responses for task listings
- **ValidationError**: Captures specific validation errors from API responses