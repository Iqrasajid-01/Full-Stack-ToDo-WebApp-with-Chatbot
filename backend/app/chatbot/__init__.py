"""
AI Chatbot Module

Provides conversational task management using Cohere LLM and MCP tools.
"""

from .routes import router as chatbot_router

__all__ = ["chatbot_router"]
