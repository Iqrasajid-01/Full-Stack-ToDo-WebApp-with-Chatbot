from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from models.base import Base


class TaskDB(Base):
    """
    Task model representing a user's todo item.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # User ID from JWT token
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default='medium')  # Add priority field with default value
    due_date = Column(DateTime(timezone=True), nullable=True)  # Add due date field
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)
    last_modified_by = Column(String, nullable=True)  # Track who made the last change


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.
    """
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = 'medium'  # Add priority field with default value
    due_date: Optional[datetime] = None  # Add due date field


class TaskRead(BaseModel):
    """
    Schema for returning task data.
    """
    id: int
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool
    priority: str = 'medium'  # Add priority field with default value
    due_date: Optional[datetime] = None  # Add due date field
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None


class TaskUpdate(BaseModel):
    """
    Schema for updating a task.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None  # Add priority field
    due_date: Optional[datetime] = None  # Add due date field


class TaskPatch(BaseModel):
    """
    Schema for patching a task (toggling completion status).
    """
    completed: bool