from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


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
    tool_calls: Optional[dict] = None

    class Config:
        from_attributes = True
