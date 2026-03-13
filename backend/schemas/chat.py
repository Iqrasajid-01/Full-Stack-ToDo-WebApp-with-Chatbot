from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for sending a message to the chatbot."""
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID to continue")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata (project_id, session_id)")


class ToolCall(BaseModel):
    """Schema for tool execution information."""
    tool: str = Field(..., description="Name of the MCP tool executed")
    parameters: Dict[str, Any] = Field(..., description="Parameters passed to the tool")
    result: Optional[Dict[str, Any]] = Field(None, description="Result from tool execution")


class ChatResponse(BaseModel):
    """Response schema from the chatbot."""
    reply: str = Field(..., description="The chatbot's response message")
    conversation_id: int = Field(..., description="The conversation ID")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="List of executed tools")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class ConversationSchema(BaseModel):
    """Schema for conversation summary."""
    id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = 0

    class Config:
        from_attributes = True


class MessageSchema(BaseModel):
    """Schema for individual message."""
    id: int
    conversation_id: int
    user_id: str
    role: str
    content: str
    created_at: datetime
    tool_calls: Optional[List[Dict]] = None

    class Config:
        from_attributes = True


class ConversationWithMessages(BaseModel):
    """Schema for conversation with message history."""
    conversation: ConversationSchema
    messages: List[MessageSchema]
