# Full-Stack Todo Application - Setup and Running Guide

## Overview
This is a full-stack todo application with:
- Frontend: Next.js application running on port 3000
- Backend: FastAPI application running on port 8000
- Database: PostgreSQL (Neon)

## Issues Fixed
1. Fixed authentication endpoints with proper password verification
2. Updated database schema to include missing 'priority' and 'last_modified_by' columns
3. Resolved internal server errors in task endpoints
4. Fixed compatibility between frontend API calls and backend endpoints

## How to Run the Application

### Prerequisites
- Python 3.8+
- Node.js 18+
- Access to the PostgreSQL database (credentials in .env files)

### Backend Setup (Port 8000)
1. Navigate to the backend directory:
   ```bash
   cd D:\Q4-Hackathon2\H2-Phase-II\backend
   ```

2. Install dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```
   
   Or use the provided script:
   ```bash
   start_server.bat
   ```

### Frontend Setup (Port 3000)
1. Navigate to the frontend directory:
   ```bash
   cd D:\Q4-Hackathon2\H2-Phase-II\frontend
   ```

2. Install dependencies (if not already installed):
   ```bash
   npm install
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```

### Accessing the Application
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
- Backend API Documentation: http://127.0.0.1:8000/docs

## API Endpoints Available
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login existing user
- `GET /api/` - Get all tasks for authenticated user
- `POST /api/` - Create a new task
- `GET /api/{task_id}` - Get a specific task
- `PUT /api/{task_id}` - Update a specific task
- `DELETE /api/{task_id}` - Delete a specific task
- `PATCH /api/{task_id}/complete` - Toggle task completion status

## Troubleshooting
If you encounter issues:
1. Make sure both backend and frontend are running
2. Check that the backend is running on port 8000
3. Check that the frontend is running on port 3000
4. Verify that the database connection is working
5. Check the .env files for correct configuration

## Verification
The application has been tested and all endpoints are working correctly:
- ✅ User registration and authentication
- ✅ Task creation, retrieval, update, and deletion
- ✅ Priority field handling
- ✅ Proper error handling
- ✅ Frontend-backend communication