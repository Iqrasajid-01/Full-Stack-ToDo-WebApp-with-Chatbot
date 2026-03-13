# Tasks: Backend – Phase II Todo Web Application

**Input**: Design documents from `/specs/001-backend-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are NOT explicitly requested in the feature specification, so test tasks will not be generated here.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/` (using backend structure as per plan.md)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project structure and initialize FastAPI in `backend/main.py`
- [ ] T002 Configure CORS for frontend communication in `backend/main.py`
- [ ] T003 Setup environment configuration loading in `backend/core/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Configure PostgreSQL connection and SQLModel engine in `backend/db/session.py`
- [ ] T005 Create database tables at startup in `backend/db/init.py`
- [ ] T006 Implement JWT validation logic in `backend/core/security.py`
- [ ] T007 Define authentication dependencies in `backend/core/dependencies.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Authenticated User Manages Tasks (Priority: P1) 🎯 MVP

**Goal**: An authenticated user can perform all CRUD operations on their own tasks, ensuring data isolation and proper authorization.

**Independent Test**: Create a user, log in, and then perform all task management operations (create, retrieve all, retrieve single, update, delete, toggle completion) for only that user. Verify that attempts to access other users' tasks fail.

### Implementation for User Story 1

- [ ] T008 [P] [US1] Define `Task` SQLModel entity in `backend/models/task.py`
- [ ] T009 [P] [US1] Define Pydantic schemas for `Task` input/output in `backend/schemas/task.py`
- [ ] T010 [US1] Implement API route to create a task in `backend/routes/tasks.py`
- [ ] T011 [US1] Implement API route to retrieve all tasks for authenticated user in `backend/routes/tasks.py`
- [ ] T012 [US1] Implement API route to retrieve a single task by ID in `backend/routes/tasks.py`
- [ ] T013 [US1] Implement API route to update a task by ID in `backend/routes/tasks.py`
- [ ] T014 [US1] Implement API route to delete a task by ID in `backend/routes/tasks.py`
- [ ] T015 [US1] Implement API route to toggle task completion status in `backend/routes/tasks.py`
- [ ] T016 [US1] Add ownership verification for update/delete operations in `backend/routes/tasks.py`
- [ ] T017 [US1] Add error handling for 401 and 403 in `backend/routes/tasks.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task Input Validation (Priority: P2)

**Goal**: The backend service validates task input to ensure data integrity and provides clear error messages for invalid input.

**Independent Test**: Attempt to create or update tasks with invalid data (e.g., empty title, incorrect data types) and verify that appropriate 400 Bad Request errors are returned with descriptive messages.

### Implementation for User Story 2

- [ ] T018 [US2] Add input validation for task title (not empty) in `backend/schemas/task.py` and `backend/routes/tasks.py`
- [ ] T019 [US2] Implement error handling for 400 Bad Request on invalid input in `backend/routes/tasks.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T020 Code cleanup and refactoring to adhere to Python PEP 8 standards
- [ ] T021 Add comprehensive logging for API requests and database operations
- [ ] T022 Review and implement any additional unit or integration tests as needed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 but is independently testable for validation logic.

### Within Each User Story

- Models before schemas
- Schemas before API routes
- Core implementation before ownership verification/error handling within a route.
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks T001-T003 can be considered for parallel execution if independent.
- Once Foundational phase (T004-T007) completes, User Story 1 (T008-T017) and User Story 2 (T018-T019) can be worked on in parallel by different team members.
- Within User Story 1, tasks T008 and T009 ([P] tasks) can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Launch all models and schemas for User Story 1 together:
Task: "Define `Task` SQLModel entity in `backend/models/task.py`"
Task: "Define Pydantic schemas for `Task` input/output in `backend/schemas/task.py`"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
