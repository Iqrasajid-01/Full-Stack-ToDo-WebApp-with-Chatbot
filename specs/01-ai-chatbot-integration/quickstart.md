# Quickstart: AI Chatbot Integration

**Feature**: AI-Native Todo SaaS Chatbot
**Date**: 2026-02-17
**Version**: 1.0.0

---

## Overview

This guide walks you through setting up and running the AI chatbot integration locally. By the end, you'll have a working chatbot that can manage tasks via natural language conversations.

**Prerequisites**:
- Python 3.11+
- Node.js 18+
- Neon PostgreSQL database
- Cohere API key
- Existing Todo backend and frontend

---

## Step 1: Environment Setup

### Backend Environment Variables

Create or update `backend/.env`:

```bash
# Database
DATABASE_URL="postgresql://user:password@host.neon.tech/dbname?sslmode=require"

# JWT Authentication (must match Better Auth secret in frontend)
JWT_SECRET="your-super-secret-jwt-key-min-32-chars"

# Cohere API
COHERE_API_KEY="your-cohere-api-key"
COHERE_MODEL="command-r-plus"

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# MCP Configuration
MCP_ENABLED=true
```

### Frontend Environment Variables

Create or update `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL="http://localhost:8000"

# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_SECRET="your-super-secret-jwt-key-min-32-chars"
NEXT_PUBLIC_AUTH_COOKIE_NAME="better-auth.session_token"

# Chatbot Configuration
NEXT_PUBLIC_CHATBOT_ENABLED=true
NEXT_PUBLIC_CHATBOT_API_URL="http://localhost:8000/api"
```

---

## Step 2: Install Dependencies

### Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Additional dependencies for chatbot (if not in requirements.txt)
pip install cohere openai-agents mcp
```

### Frontend

```bash
cd frontend

# Install Node.js dependencies
npm install

# Additional dependencies for chatbot (if needed)
npm install ai @ai-sdk/react
```

---

## Step 3: Database Migration

Run the database migration to create Conversation and Message tables:

```bash
cd backend

# Using SQLModel (if using SQLModel's built-in migration)
python -m db.init

# OR using Alembic (if using Alembic migrations)
alembic upgrade head

# OR manually run migration script
python migrate_chatbot_tables.py
```

**Verify tables created**:

```sql
-- Connect to your Neon database
\c your_database

-- List tables
\dt

-- Should see:
-- conversations
-- messages
-- tasks
-- users
-- (and any existing tables)
```

---

## Step 4: Start Backend Server

```bash
cd backend

# Option 1: Using the run script
python run_server.py

# Option 2: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using the batch file (Windows)
start_server.bat
```

**Verify backend is running**:

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

---

## Step 5: Start Frontend Server

```bash
cd frontend

# Development mode
npm run dev

# Production build (optional)
npm run build
npm run start
```

**Verify frontend is running**:

Open browser to `http://localhost:3000`

---

## Step 6: Test Authentication

Before testing the chatbot, ensure you're authenticated:

1. Open `http://localhost:3000` in your browser
2. Log in to the Todo application (or create an account)
3. Verify you can see your tasks
4. Open browser DevTools → Application → Cookies
5. Verify `better-auth.session_token` cookie exists

---

## Step 7: Test Chatbot

### Test 1: Open Chatbot Interface

1. Look for the floating chatbot button (bottom-right corner)
2. Click the button to open the chat window
3. You should see a greeting message from the AI

### Test 2: Create a Task

**Input**:
```
Add a task to buy groceries tomorrow
```

**Expected Response**:
```
I've created a new task: "Buy groceries" for tomorrow. Is there anything else you'd like me to help you with?
```

**Verification**:
- Check the Todo UI - the new task should appear
- Task should have due date set to tomorrow

### Test 3: List Tasks

**Input**:
```
Show me my tasks
```

**Expected Response**:
```
You have 3 tasks:

1. ✅ Buy groceries (due: tomorrow)
2. ⏳ Call dentist (due: Feb 20)
3. ⏳ Finish project report (due: Feb 25)

Would you like me to help you with any of these?
```

### Test 4: Complete a Task

**Input**:
```
Mark the grocery task as done
```

**Expected Response**:
```
Great job! I've marked "Buy groceries" as completed. You now have 2 pending tasks remaining.
```

**Verification**:
- Check the Todo UI - the task should show as completed

### Test 5: Multi-turn Conversation

**Input 1**:
```
I need to plan my day
```

**Response 1**:
```
I'd be happy to help you plan your day! You currently have 2 pending tasks:
1. Call dentist
2. Finish project report

Would you like to add more tasks or prioritize these?
```

**Input 2**:
```
Add a task to exercise for 30 minutes
```

**Response 2**:
```
I've added "Exercise for 30 minutes" to your tasks. Would you like to set a specific time for this?
```

---

## Step 8: Verify Conversation History

1. Close the chatbot window
2. Refresh the page
3. Reopen the chatbot window
4. Your conversation history should still be visible

---

## Troubleshooting

### Issue: Chatbot button not visible

**Solution**:
- Verify `NEXT_PUBLIC_CHATBOT_ENABLED=true` in frontend `.env.local`
- Check browser console for JavaScript errors
- Ensure `ChatbotButton` component is imported in main layout

### Issue: "Unauthorized" error

**Solution**:
- Verify you're logged in to the Todo application
- Check JWT_SECRET matches in both backend and frontend
- Verify `better-auth.session_token` cookie exists
- Check browser console for authentication errors

### Issue: "Cohere API error"

**Solution**:
- Verify `COHERE_API_KEY` is set correctly in backend `.env`
- Check Cohere API key is valid: https://dashboard.cohere.com/api-keys
- Verify internet connection
- Check Cohere API status: https://status.cohere.com/

### Issue: "Task not found" error

**Solution**:
- Verify the task exists in your account
- Check user isolation is enforced (can't access other users' tasks)
- Try listing tasks first: "Show me my tasks"

### Issue: Database connection error

**Solution**:
- Verify `DATABASE_URL` is correct in backend `.env`
- Check Neon database is accessible
- Verify SSL mode is set: `?sslmode=require`
- Test connection: `python test_db_connection.py`

### Issue: MCP tools not executing

**Solution**:
- Verify MCP server is initialized in `main.py`
- Check MCP tools are registered
- Look for MCP-related errors in backend logs
- Ensure `MCP_ENABLED=true` in `.env`

---

## Development Tips

### Enable Debug Logging

Add to backend `.env`:

```bash
LOG_LEVEL=DEBUG
```

View logs:

```bash
# Backend logs
tail -f backend/logs/app.log

# Or if running in foreground
# Logs appear in terminal
```

### Test API Directly

```bash
# Get JWT token (development only)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/test-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user"}' | jq -r '.token')

# Send chatbot message
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test"}'
```

### Database Inspection

```bash
# Connect to Neon database
psql "$DATABASE_URL"

# View conversations
SELECT * FROM conversations WHERE user_id = 'your-user-id';

# View messages
SELECT * FROM messages WHERE conversation_id = 1 ORDER BY created_at;

# View recent tool calls
SELECT content, tool_calls FROM messages 
WHERE role = 'assistant' AND tool_calls IS NOT NULL
ORDER BY created_at DESC LIMIT 10;
```

---

## Performance Testing

### Load Test with Apache Bench

```bash
# Test chatbot endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -p chatbot-payload.json \
  http://localhost:8000/api/chatbot/message
```

### Expected Performance

- Chatbot response time: < 5 seconds (p95)
- Task operations: < 2 seconds (p95)
- Conversation history load: < 2 seconds
- Concurrent users: 100 without degradation

---

## Next Steps

1. **Customize Chatbot Personality**: Modify system instructions in `backend/app/chatbot/agent.py`
2. **Add More Tools**: Extend MCP server with additional capabilities
3. **Improve UI**: Customize chatbot appearance in `frontend/src/components/Chatbot/`
4. **Add Analytics**: Track chatbot usage and user satisfaction
5. **Deploy to Production**: Follow deployment guide for production setup

---

## Additional Resources

- [API Documentation](./contracts/chat-api.yaml)
- [MCP Tool Contracts](./contracts/mcp-tools.yaml)
- [Data Model](./data-model.md)
- [Architecture Plan](./plan.md)
- [Feature Specification](../01-ai-chatbot-integration/spec.md)

---

## Support

If you encounter issues not covered in this guide:

1. Check the troubleshooting section above
2. Review backend logs for error messages
3. Check frontend browser console for errors
4. Verify all environment variables are set correctly
5. Consult the architecture documentation

**Common Commands**:

```bash
# Restart backend
cd backend && python run_server.py

# Restart frontend
cd frontend && npm run dev

# Check database connection
cd backend && python test_db_connection.py

# View backend logs
tail -f backend/logs/app.log

# Clear conversation history (development only)
cd backend && python -c "from db.session import session; from models.conversation import Conversation; session.query(Conversation).delete(); session.commit()"
```

---

**Congratulations!** 🎉 Your AI chatbot is now ready to help you manage tasks through natural language conversations!
