import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db.init import create_db_and_tables
from core.config import settings
import os
from dotenv import load_dotenv
from cachetools import TTLCache
from threading import Lock
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from db.session import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Load environment variables
load_dotenv()

# Create a cache with TTL (time-to-live)
# Cache up to 1000 items for 5 minutes (300 seconds)
task_cache = TTLCache(maxsize=1000, ttl=300)
cache_lock = Lock()

# Import routes
from routes import tasks, auth

# Create FastAPI app
app = FastAPI(
    title="Todo Backend Service",
    description="Backend service for the Todo web application",
    version="0.1.0"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Add security headers using custom middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    # Only add security headers to non-documentation routes
    if not request.url.path.startswith('/docs') and not request.url.path.startswith('/redoc'):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",  # Explicitly allow localhost:3000
        "http://127.0.0.1:3000",  # Also allow 127.0.0.1:3000
        "*"  # Allow all origins during development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Add exposed headers to allow frontend to access response headers
    expose_headers=["Access-Control-Allow-Origin", "Authorization"]
)

# Event handler to create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Exception handlers for consistent error responses
# Updated to preserve actual error messages from routes
@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: Exception):
    # Only return generic message if no detail is available
    if hasattr(exc, 'detail'):
        detail = exc.detail
    else:
        detail = "Bad Request"
    return JSONResponse(
        status_code=400,
        content={
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: Exception):
    if hasattr(exc, 'detail'):
        detail = exc.detail
    else:
        detail = "Unauthorized"
    return JSONResponse(
        status_code=401,
        content={
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@app.exception_handler(403)
async def forbidden_handler(request: Request, exc: Exception):
    if hasattr(exc, 'detail'):
        detail = exc.detail
    else:
        detail = "Forbidden"
    return JSONResponse(
        status_code=403,
        content={
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    if hasattr(exc, 'detail'):
        detail = exc.detail
    else:
        detail = "Not Found"
    return JSONResponse(
        status_code=404,
        content={
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    # Log the actual error for debugging
    logger.error(f"Internal server error: {exc}", exc_info=True)
    if hasattr(exc, 'detail'):
        detail = exc.detail
    else:
        detail = "Internal Server Error"
    return JSONResponse(
        status_code=500,
        content={
            "detail": detail,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

# Include routes
app.include_router(tasks.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")

# Include Better Auth compatible routes at root level
app.include_router(auth.better_auth_router)

# Include chatbot routes
try:
    from app.chatbot.routes import router as chatbot_router
    app.include_router(chatbot_router, prefix="/api")
    logger.info("Chatbot routes included successfully")
except ImportError as e:
    logger.warning(f"Chatbot routes not available: {e}")

# Include MCP server routes
try:
    from mcp.main import app as mcp_app
    app.mount("/mcp", mcp_app)
    logger.info("MCP server mounted successfully")
except ImportError:
    logger.warning("MCP server not found, skipping mount")
except Exception as e:
    logger.error(f"Failed to mount MCP server: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo Backend Service"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}