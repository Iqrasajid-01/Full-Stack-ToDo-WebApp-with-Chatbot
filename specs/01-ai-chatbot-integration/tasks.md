# Tasks: AI Chatbot Integration

**Input**: Design documents from `/specs/01-ai-chatbot-integration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not included by default. Add test tasks if TDD approach is requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/`, `backend/app/`, `backend/mcp/`, `backend/models/`, `backend/schemas/`
- **Frontend**: `frontend/`, `frontend/src/`, `frontend/src/components/`, `frontend/src/services/`
- Paths follow the structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [X] T001 [P] Install backend dependencies: cohere, openai-agents, mcp in backend/requirements.txt
- [ ] T002 [P] Install frontend dependencies for chatbot components in frontend/package.json
- [ ] T003 [P] Add environment variables to backend/.env: COHERE_API_KEY, COHERE_MODEL, MCP_ENABLED
- [ ] T004 [P] Add environment variables to frontend/.env.local: NEXT_PUBLIC_CHATBOT_ENABLED, NEXT_PUBLIC_CHATBOT_API_URL
- [X] T005 [P] Update backend/.gitignore to exclude .env and sensitive files
- [X] T006 [P] Update frontend/.gitignore to exclude .env.local and sensitive files (already exists)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 [P] Create Conversation model in backend/models/conversation.py (id, user_id, title, created_at, updated_at)
- [X] T008 [P] Create Message model in backend/models/message.py (id, conversation_id, user_id, role, content, created_at, tool_calls)
- [ ] T009 Create database migration for conversations and messages tables in backend/db/migrations/
- [X] T010 [P] Create ChatRequest schema in backend/schemas/chat.py
- [X] T011 [P] Create ChatResponse schema in backend/schemas/chat.py
- [X] T012 [P] Create ConversationSchema in backend/schemas/conversation.py
- [X] T013 [P] Create MessageSchema in backend/schemas/conversation.py
- [X] T014 [P] Add COHERE_API_KEY and COHERE_MODEL to backend/core/config.py
- [X] T015 [P] Create backend/app/chatbot/__init__.py module initialization
- [X] T016 [P] Create backend/mcp/tools/__init__.py for MCP tool exports
- [X] T017 [P] Create frontend/src/types/chatbot.ts TypeScript types (ChatMessage, ChatRequest, ChatResponse, Conversation)
- [X] T018 [P] Create frontend/src/services/chatbot.ts API client (sendMessage, getConversations, getConversation)
- [X] T019 Setup logging infrastructure in backend/app/chatbot/logger.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Tasks via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks by typing natural language commands in the chatbot

**Independent Test**: User can type "Add a task to buy groceries tomorrow" and see a new task created with appropriate details

### Implementation for User Story 1

- [ ] T020 [P] [US1] Create CohereAdapter class in backend/app/chatbot/cohere_adapter.py (send_message, parse_response methods)
- [ ] T021 [P] [US1] Create add_task MCP tool in backend/mcp/tools/add_task.py (user_id validation, task creation, error handling)
- [ ] T022 [US1] Implement OpenAI Agents SDK agent in backend/app/chatbot/agent.py (agent configuration, tool registration)
- [ ] T023 [US1] Create POST /api/chatbot/message endpoint in backend/app/chatbot/routes.py
- [ ] T024 [US1] Implement message storage logic in backend/app/chatbot/session.py (store user message, store assistant response)
- [ ] T025 [US1] Create ChatbotButton component in frontend/src/components/Chatbot/ChatbotButton.tsx (floating button, bottom-right)
- [ ] T026 [US1] Create ChatbotWindow component in frontend/src/components/Chatbot/ChatbotWindow.tsx (chat panel, message display)
- [ ] T027 [US1] Create ChatMessage component in frontend/src/components/Chatbot/ChatMessage.tsx (individual message styling)
- [ ] T028 [US1] Create ChatInput component in frontend/src/components/Chatbot/ChatInput.tsx (text input, send button)
- [ ] T029 [US1] Create useChatbot hook in frontend/src/components/Chatbot/useChatbot.ts (state management, API calls, loading states)
- [ ] T030 [US1] Integrate ChatbotButton into main layout in frontend/src/app/(main)/layout.tsx
- [ ] T031 [US1] Add user story 1 logging in backend/app/chatbot/routes.py and backend/mcp/tools/add_task.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently
- User can click chatbot button, open chat window, type "Add a task to buy groceries", and see task created

---

## Phase 4: User Story 2 - List and View Tasks via Chat (Priority: P1)

**Goal**: Users can ask the chatbot to show their tasks and receive a formatted list

**Independent Test**: User can type "Show me my tasks" and receive a formatted list of their tasks with status and details

### Implementation for User Story 2

- [ ] T032 [P] [US2] Create list_tasks MCP tool in backend/mcp/tools/list_tasks.py (user_id filtering, status filtering, pagination)
- [ ] T033 [US2] Update agent in backend/app/chatbot/agent.py to recognize list task requests
- [ ] T034 [US2] Update CohereAdapter in backend/app/chatbot/cohere_adapter.py to handle list_tasks tool calls
- [ ] T035 [US2] Update ChatMessage component to display task lists with formatting (status icons, due dates)
- [ ] T036 [US2] Add user story 2 logging in backend/mcp/tools/list_tasks.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently
- User can create tasks AND list tasks via chatbot

---

## Phase 5: User Story 3 - Complete and Delete Tasks via Chat (Priority: P2)

**Goal**: Users can mark tasks as complete or delete them using natural language commands

**Independent Test**: User can type "Mark task 3 as done" or "Delete the grocery shopping task" and see the action performed

### Implementation for User Story 3

- [ ] T037 [P] [US3] Create complete_task MCP tool in backend/mcp/tools/complete_task.py (user ownership validation, status update)
- [ ] T038 [P] [US3] Create delete_task MCP tool in backend/mcp/tools/delete_task.py (user ownership validation, task deletion)
- [ ] T039 [US3] Update agent in backend/app/chatbot/agent.py to recognize complete/delete requests
- [ ] T040 [US3] Update CohereAdapter to handle complete_task and delete_task tool calls
- [ ] T041 [US3] Update ChatMessage component to show completion/deletion confirmations
- [ ] T042 [US3] Add user story 3 logging in backend/mcp/tools/complete_task.py and backend/mcp/tools/delete_task.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently
- User can create, list, complete, and delete tasks via chatbot

---

## Phase 6: User Story 4 - Update Tasks via Chat (Priority: P2)

**Goal**: Users can modify existing tasks through natural language commands

**Independent Test**: User can type "Change the due date for task 2 to next Monday" and see the task updated

### Implementation for User Story 4

- [ ] T043 [P] [US4] Create update_task MCP tool in backend/mcp/tools/update_task.py (field validation, ownership check, partial updates)
- [ ] T044 [US4] Update agent in backend/app/chatbot/agent.py to recognize update requests
- [ ] T045 [US4] Update CohereAdapter to handle update_task tool calls with multiple parameters
- [ ] T046 [US4] Update ChatMessage component to show update confirmations with changed fields
- [ ] T047 [US4] Add user story 4 logging in backend/mcp/tools/update_task.py

**Checkpoint**: All core task operations (create, list, complete, delete, update) should now work via chatbot

---

## Phase 7: User Story 5 - Maintain Conversation History (Priority: P3)

**Goal**: The chatbot remembers conversations and maintains context across sessions

**Independent Test**: User can close and reopen the chat, and the chatbot retains the conversation history

### Implementation for User Story 5

- [ ] T048 [P] [US5] Create GET /api/chatbot/conversations endpoint in backend/app/chatbot/routes.py (list user conversations)
- [ ] T049 [P] [US5] Create GET /api/chatbot/conversations/{conversation_id} endpoint (load conversation with messages)
- [ ] T050 [US5] Update useChatbot hook to load conversation history on chat window open
- [ ] T051 [US5] Update ChatbotWindow to display loaded conversation history
- [ ] T052 [US5] Implement conversation title auto-generation in backend/app/chatbot/session.py (based on first message)
- [ ] T053 [US5] Add conversation switching UI in ChatbotWindow (dropdown or list of recent conversations)
- [ ] T054 [US5] Add user story 5 logging in backend/app/chatbot/routes.py

**Checkpoint**: All user stories should now be independently functional
- Full chatbot with conversation history, context, and all task operations

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T055 [P] Update backend/README.md with chatbot module documentation
- [ ] T056 [P] Update frontend/README.md with chatbot component documentation
- [ ] T057 [P] Add error boundary components in frontend/src/components/Chatbot/ChatErrorBoundary.tsx
- [ ] T058 [P] Add loading skeletons in frontend/src/components/Chatbot/ChatLoadingSkeleton.tsx
- [ ] T059 [P] Implement rate limiting middleware in backend/core/security.py
- [ ] T060 [P] Add health check endpoint in backend/app/chatbot/routes.py (GET /api/chatbot/health)
- [ ] T061 [P] Update quickstart.md with actual setup instructions post-implementation
- [ ] T062 [P] Run through all acceptance scenarios from spec.md and verify each one passes
- [ ] T063 [P] Performance optimization: Add database indexes for conversation and message queries
- [ ] T064 [P] Security review: Verify all endpoints enforce JWT authentication and user isolation
- [ ] T065 [P] Add TypeScript ESLint configuration for chatbot components in frontend/
- [ ] T066 [P] Add Ruff/Black configuration for Python chatbot code in backend/
- [ ] T067 [P] Create ADR for Cohere adapter pattern in specs/01-ai-chatbot-integration/adr-cohere-adapter.md
- [ ] T068 [P] Create ADR for MCP tool architecture in specs/01-ai-chatbot-integration/adr-mcp-tools.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 (agent, adapter)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1/US2
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Integrates with previous stories
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Depends on conversation persistence from foundation

### Within Each User Story

- Models/tools before agent updates
- Backend before frontend
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: All tasks T001-T006 can run in parallel
- **Phase 2 (Foundational)**: 
  - T007, T008 (models) can run in parallel
  - T010, T011, T012, T013 (schemas) can run in parallel
  - T017, T018 (frontend types/services) can run in parallel
- **Phase 3+ (User Stories)**:
  - MCP tools (T021, T032, T037, T038, T043) can be developed in parallel by different developers
  - Frontend components (T025, T026, T027, T028) can be developed in parallel
  - Different user stories can be worked on in parallel once foundation is complete

---

## Parallel Example: User Story 1

```bash
# Launch all models/tools for User Story 1 together:
Task: "Create CohereAdapter class in backend/app/chatbot/cohere_adapter.py"
Task: "Create add_task MCP tool in backend/mcp/tools/add_task.py"

# Launch all frontend components for User Story 1 together:
Task: "Create ChatbotButton component in frontend/src/components/Chatbot/ChatbotButton.tsx"
Task: "Create ChatbotWindow component in frontend/src/components/Chatbot/ChatbotWindow.tsx"
Task: "Create ChatMessage component in frontend/src/components/Chatbot/ChatMessage.tsx"
Task: "Create ChatInput component in frontend/src/components/Chatbot/ChatInput.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T019) - **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T020-T031)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Can user create a task via chatbot?
   - Is task visible in main Todo UI?
   - Is conversation persisted?
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (create tasks)
   - Developer B: User Story 2 (list tasks)
   - Developer C: User Story 3 (complete/delete tasks)
3. Stories complete and integrate independently through shared agent and adapter

---

## Task Summary

| Phase | Description | Task Count |
|-------|-------------|------------|
| Phase 1 | Setup | 6 tasks |
| Phase 2 | Foundational | 13 tasks |
| Phase 3 | User Story 1 (Create) | 12 tasks |
| Phase 4 | User Story 2 (List) | 5 tasks |
| Phase 5 | User Story 3 (Complete/Delete) | 6 tasks |
| Phase 6 | User Story 4 (Update) | 5 tasks |
| Phase 7 | User Story 5 (History) | 7 tasks |
| Phase 8 | Polish | 14 tasks |
| **Total** | | **68 tasks** |

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MCP tools enforce user isolation - always validate user_id from JWT
- Cohere API key must be stored securely, never in code or logs
- Conversation persistence is stateless - load from DB on each request

---

## Quick Reference: File Paths

### Backend

- Models: `backend/models/conversation.py`, `backend/models/message.py`
- Schemas: `backend/schemas/chat.py`, `backend/schemas/conversation.py`
- Chatbot: `backend/app/chatbot/{agent.py, cohere_adapter.py, tools.py, schemas.py, routes.py, session.py}`
- MCP Tools: `backend/mcp/tools/{add_task.py, list_tasks.py, complete_task.py, delete_task.py, update_task.py}`

### Frontend

- Types: `frontend/src/types/chatbot.ts`
- Services: `frontend/src/services/chatbot.ts`
- Components: `frontend/src/components/Chatbot/{ChatbotButton.tsx, ChatbotWindow.tsx, ChatMessage.tsx, ChatInput.tsx, useChatbot.ts}`
