from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
# Get the directory where this config.py file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "..", ".env")  # .env is in the backend directory
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    NEON_DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_HOSTS: str = "http://localhost:3000"
    
    # Cohere API settings for AI chatbot
    COHERE_API_KEY: Optional[str] = None
    COHERE_MODEL: str = "command-r-plus"
    
    # MCP settings
    MCP_ENABLED: bool = True

    class Config:
        env_file = env_path


# Create settings instance
settings = Settings()