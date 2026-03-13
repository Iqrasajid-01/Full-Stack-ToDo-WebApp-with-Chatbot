from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Task-related schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"
    due_date: Optional[str] = None


class TaskCreate(TaskBase):
    title: str  # Required field
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime


class TaskToggleComplete(BaseModel):
    completed: bool


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    offset: int
    limit: int


# Response schemas for API endpoints
class SuccessResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    timestamp: str