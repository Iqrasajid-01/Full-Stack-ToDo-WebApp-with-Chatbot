from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Test Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Server is running!"}

@app.get("/health")
def health_check():
    logger.info("Health endpoint accessed")
    return {"status": "healthy"}

@app.post("/sign-up")
async def signup_endpoint():
    logger.info("Sign-up endpoint accessed")
    return {"message": "Sign-up endpoint reached"}

if __name__ == "__main__":
    logger.info("Starting server on http://localhost:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")