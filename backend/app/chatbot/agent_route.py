"""
AI Chatbot Agent Endpoint

Internal endpoint for AI agent processing.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.chatbot.agent import process_chat_message
from app.chatbot.logger import chatbot_logger

router = APIRouter(prefix="/chatbot", tags=["chatbot-internal"])

logger = chatbot_logger


class AgentRequest(BaseModel):
    """Request for agent processing."""
    message: str
    user_id: str
    conversation_id: int


class AgentResponse(BaseModel):
    """Response from agent processing."""
    reply: str
    tool_calls: Optional[list] = None


@router.post("/agent", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    """
    Internal endpoint for AI agent processing.
    This is called by the main chatbot message endpoint.
    """
    try:
        result = await process_chat_message(
            message=request.message,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        return AgentResponse(
            reply=result["reply"],
            tool_calls=result.get("tool_calls")
        )
        
    except Exception as e:
        logger.error(f"Error in agent endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
