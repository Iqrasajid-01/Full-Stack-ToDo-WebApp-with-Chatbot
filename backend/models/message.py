from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from models.base import Base


class Message(Base):
    """
    Represents an individual message within a conversation.

    Purpose: Store the complete conversation history between user and AI assistant.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    tool_calls = Column(JSON, nullable=True)  # List of tool call dicts

    # Relationships - use back_populates with proper string reference
    conversation = relationship(
        "Conversation",
        back_populates="messages",
        lazy="joined"
    )

    # Add check constraint for role
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="check_message_role"),
    )
