from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Task(SQLModel, table=True):
    """
    Task model representing a user's todo item.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # User ID from JWT token
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    last_modified_by: Optional[str] = Field(default=None)  # Track who made the last change


# Separate Pydantic models for API schemas
from pydantic import BaseModel


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.
    """
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskRead(BaseModel):
    """
    Schema for returning task data.
    """
    id: int
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime
    last_modified_by: Optional[str] = None


class TaskUpdate(BaseModel):
    """
    Schema for updating a task.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskPatch(BaseModel):
    """
    Schema for patching a task (toggling completion status).
    """
    completed: bool