# Data Model: AI Chatbot Integration

**Feature**: AI-Native Todo SaaS Chatbot
**Date**: 2026-02-17
**Version**: 1.0

---

## Overview

This document defines the database schema for the AI chatbot integration. The chatbot uses two new entities (Conversation and Message) that integrate with the existing Todo application's User and Task entities.

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    User     │       │   Conversation   │       │   Message   │
├─────────────┤       ├──────────────────┤       ├─────────────┤
│ id (PK)     │───┐   │ id (PK)          │───┐   │ id (PK)     │
│ email       │   │   │ user_id (FK)     │   │   │ conversation│
│ name        │   └──>│ title            │   └──>│ user_id (FK)│
│ created_at  │       │ created_at       │       │ role        │
│ updated_at  │       │ updated_at       │       │ content     │
└─────────────┘       └──────────────────┘       │ created_at  │
         ▲                                        │ tool_calls  │
         │                              ┌─────────┴─────────────┤
         │                              │      Task (existing)  │
         │                              ├───────────────────────┤
         └──────────────────────────────│ user_id (FK) <────────┘
                                        │ id, title, description│
                                        │ status, due_date      │
                                        └───────────────────────┘
```

---

## Entity Definitions

### Conversation

Represents a chat session between a user and the AI chatbot.

**Purpose**: Container for organizing messages into logical conversation threads.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique conversation identifier |
| user_id | String | NOT NULL, Indexed, Foreign Key → User.id | Owner of the conversation (JWT subject) |
| title | String | NOT NULL, Default: "New Conversation" | Conversation title (auto-generated or user-provided) |
| created_at | DateTime | NOT NULL, Default: UTC now, Indexed | When the conversation was created |
| updated_at | DateTime | NOT NULL, Default: UTC now, On update: SET NOW | Last activity timestamp |

**Indexes**:
- `idx_conversations_user_id` - Fast filtering by user
- `idx_conversations_created_at` - Chronological ordering
- `idx_conversations_user_created` - Composite: (user_id, created_at DESC)

**Relationships**:
- **Belongs to**: User (many-to-one)
- **Has many**: Message (one-to-many, cascade delete)

**Validation Rules**:
- user_id MUST be a valid UUID from authenticated JWT
- title MUST be 1-200 characters
- created_at MUST be <= updated_at
- User can have unlimited conversations

**State Transitions**:
- **Created**: When user sends first message to chatbot
- **Active**: When conversation has recent messages (< 7 days)
- **Archived**: When conversation has no messages for > 30 days (optional future feature)
- **Deleted**: When user explicitly deletes conversation (cascade deletes messages)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .message import Message

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(..., index=True, description="JWT user identifier")
    title: str = Field(default="New Conversation", max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True
    )
```

---

### Message

Represents an individual message within a conversation.

**Purpose**: Store the complete conversation history between user and AI assistant.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique message identifier |
| conversation_id | Integer | NOT NULL, Foreign Key → Conversation.id | Parent conversation |
| user_id | String | NOT NULL, Indexed | Denormalized user ownership for fast filtering |
| role | String | NOT NULL, Enum: "user" | "assistant" | Message sender |
| content | Text | NOT NULL | Full message content (supports long text) |
| created_at | DateTime | NOT NULL, Default: UTC now, Indexed | Message timestamp |
| tool_calls | JSON | Optional | Structured tool call data if assistant invoked tools |

**Indexes**:
- `idx_messages_conversation_id` - Fast lookup by conversation
- `idx_messages_user_id` - Filter by user across conversations
- `idx_messages_created_at` - Chronological ordering
- `idx_messages_conv_created` - Composite: (conversation_id, created_at ASC)

**Relationships**:
- **Belongs to**: Conversation (many-to-one)
- **Belongs to**: User (many-to-one, denormalized)

**Validation Rules**:
- conversation_id MUST reference existing Conversation
- user_id MUST match Conversation.user_id (enforced by application)
- role MUST be "user" or "assistant"
- content MUST be 1-10000 characters (truncated if longer)
- tool_calls MUST be valid JSON if present

**tool_calls JSON Structure**:
```json
{
  "calls": [
    {
      "tool": "add_task",
      "parameters": {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread"
      },
      "result": {
        "id": 123,
        "status": "success"
      }
    }
  ]
}
```

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, Text
from datetime import datetime
from typing import Optional, Dict

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(..., foreign_key="conversations.id", index=True)
    user_id: str = Field(..., index=True, description="Denormalized user ownership")
    role: str = Field(..., description="Message sender: 'user' or 'assistant'")
    content: str = Field(..., sa_column=Column(Text), description="Message content")
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    tool_calls: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    
    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

---

## Integration with Existing Schema

### User Entity (Existing)

The existing User entity is referenced but not modified:

```python
# Existing User model (reference only)
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(..., primary_key=True)  # UUID from Better Auth
    email: str = Field(..., unique=True, index=True)
    name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # New relationships (added by chatbot feature)
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="user")
```

### Task Entity (Existing)

The existing Task entity is used by MCP tools but not modified:

```python
# Existing Task model (reference only)
class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(..., foreign_key="users.id", index=True)
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending")  # pending, completed, deleted
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Database Migrations

### Migration: Create Conversations and Messages Tables

```sql
-- Create conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for conversations
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_user_created ON conversations(user_id, created_at DESC);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tool_calls JSONB
);

-- Create indexes for messages
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at ASC);

-- Add foreign key constraint for user_id (references users table)
ALTER TABLE conversations ADD CONSTRAINT fk_conversations_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE messages ADD CONSTRAINT fk_messages_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

### SQLModel Migration (Alembic)

```python
"""create conversations and messages tables

Revision ID: chatbot_integration
Revises: previous_revision
Create Date: 2026-02-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False, 
                  server_default='New Conversation'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, 
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, 
                  server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_created_at', 'conversations', ['created_at'])
    op.create_index('idx_conversations_user_created', 'conversations', 
                    ['user_id', sa.desc('created_at')])
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, 
                  server_default=sa.func.now()),
        sa.Column('tool_calls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], 
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_message_role')
    )
    
    # Create indexes
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])
    op.create_index('idx_messages_conv_created', 'messages', 
                    ['conversation_id', sa.asc('created_at')])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Query Patterns

### Common Queries

**Get all conversations for a user**:
```python
conversations = await session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.created_at.desc())
)
```

**Get messages for a conversation (with pagination)**:
```python
messages = await session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .where(Message.user_id == user_id)  # Enforce isolation
    .order_by(Message.created_at.asc())
    .offset(offset)
    .limit(limit)
)
```

**Get recent messages (last 50)**:
```python
recent_messages = await session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .where(Message.user_id == user_id)
    .order_by(Message.created_at.desc())
    .limit(50)
)
# Reverse to get chronological order
messages = list(reversed(recent_messages.all()))
```

**Create a new conversation with first message**:
```python
async with session.begin():
    conversation = Conversation(user_id=user_id, title="New Conversation")
    session.add(conversation)
    await session.flush()  # Get conversation.id
    
    message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=user_message
    )
    session.add(message)
    
    await session.commit()
    await session.refresh(conversation)
```

**Update conversation timestamp on activity**:
```python
conversation.updated_at = datetime.utcnow()
session.add(conversation)
await session.commit()
```

**Delete a conversation (cascade deletes messages)**:
```python
conversation = await session.get(Conversation, conversation_id)
if conversation and conversation.user_id == user_id:  # Enforce isolation
    await session.delete(conversation)
    await session.commit()
```

---

## Data Retention

**Active Conversations**: Retained indefinitely while user account is active.

**Archived Conversations**: Future feature - conversations older than 90 days with no activity may be archived (compressed storage).

**Deleted Conversations**: Immediately removed from database (CASCADE deletes messages).

**User Account Deletion**: All conversations and messages are CASCADE deleted when user account is deleted.

---

## Security Considerations

**User Isolation**:
- All queries MUST include `user_id` filter
- Application layer validates user owns conversation before accessing messages
- MCP tools receive user_id from JWT, never from request body

**Data Sensitivity**:
- Messages may contain sensitive task information
- Database encryption at rest recommended
- HTTPS required for all API communication

**Audit Trail**:
- All message creation is logged with timestamp
- tool_calls JSON provides audit trail for AI actions
- Consider adding `ip_address` field for compliance requirements

---

## Performance Optimization

**Indexing Strategy**:
- All foreign keys indexed
- User_id indexed for isolation filtering
- Composite indexes for common query patterns
- created_at indexed for chronological ordering

**Query Optimization**:
- Always filter by user_id first (isolation)
- Use pagination for long conversations
- Limit message history to 50 messages per request
- Consider materialized views for conversation statistics

**Caching**:
- Cache conversation metadata (title, last message time)
- No caching for message content (real-time requirement)
- Consider Redis for frequently accessed conversations

---

## Testing Considerations

**Test Data**:
- Create test users with isolated conversations
- Test with large message volumes (1000+ messages)
- Test concurrent conversation access
- Test cascade delete behavior

**Performance Tests**:
- Measure query time with 10k conversations
- Measure query time with 100k messages per conversation
- Validate index effectiveness with EXPLAIN ANALYZE

**Security Tests**:
- Verify user cannot access another user's conversations
- Verify user cannot access messages without matching user_id
- Test SQL injection prevention in message content
