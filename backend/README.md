# Backend – Phase II Todo Web Application

## Overview
This is the backend service for the Todo web application. It provides secure, scalable REST APIs for managing user tasks with JWT-based authentication and PostgreSQL persistence.

## Tech Stack
- **Framework**: FastAPI (Python)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Authentication**: JWT-based authentication
- **Data validation**: Pydantic models

## Prerequisites
- Python 3.9+
- PostgreSQL database (Neon Serverless recommended)
- JWT secret key for token validation

## Setup Instructions

1. Clone the repository
2. Navigate to the backend directory: `cd backend`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Set environment variables by copying `.env.example` to `.env` and updating values
7. Run the application: `uvicorn main:app --reload`

## Running the Application

### Using Uvicorn
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Available Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `/api/tasks` - Task management endpoints (requires authentication)

## Environment Variables
- `NEON_DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT token validation
- `ALGORITHM` - Algorithm used for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `FRONTEND_URL` - URL of the frontend application for CORS

## API Usage Examples

### Creating a Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "Sample Task", "description": "This is a sample task"}'
```

### Getting All Tasks
```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## Project Structure
```
backend/
├── main.py                # FastAPI entry point
├── core/
│   ├── config.py          # Environment configuration
│   ├── security.py        # JWT validation logic
│   └── dependencies.py    # Auth and DB dependencies
├── models/
│   └── task.py            # SQLModel Task entity
├── schemas/
│   └── task.py            # Request/Response schemas
├── routes/
│   └── tasks.py           # Task API routes
└── db/
    ├── session.py         # Database session management
    └── init.py            # Database initialization
```

## Development Commands

### Code Formatting
```bash
# Using black
black .

# Using ruff (if configured)
ruff check .
ruff format .
```

### Linting
```bash
# Using flake8
flake8 .

# Using ruff
ruff check .
```

### Type Checking
```bash
mypy .
```