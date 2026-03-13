import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import Response
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session
from typing import List, Optional
from core.dependencies import get_current_user
from db.session import get_session
from models.task import TaskDB as Task, TaskCreate, TaskUpdate, TaskRead
from datetime import datetime
from functools import wraps
from slowapi import Limiter
from slowapi.util import get_remote_address

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


def cached(timeout: int = 300):
    """
    Decorator for caching responses.
    """
    cache = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create a cache key based on function name and arguments
            cache_key = f"{func.__name__}:{str(kwargs)}"
            
            # Check if result is in cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                # Check if cache is still valid
                if (datetime.utcnow() - timestamp).seconds < timeout:
                    return result
                else:
                    # Remove expired cache entry
                    del cache[cache_key]
            
            # Call the original function
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Store result in cache with timestamp
            cache[cache_key] = (result, datetime.utcnow())
            return result
        
        return wrapper
    return decorator


@router.get("/", response_model=List[TaskRead])
@limiter.limit("20/minute")
def read_tasks(
    request: Request,
    current_user: str = Depends(get_current_user),
    completed: bool = Query(None, description="Filter by completion status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    sort_by: str = Query("created_at", description="Sort by field (created_at, updated_at, title)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    search: str = Query(None, description="Search term for title or description"),
    session: Session = Depends(get_session)
):
    """
    Retrieve all tasks for the authenticated user.
    """
    logger.info(f"Fetching tasks for user {current_user}")
    
    # Build the query with filters
    query = session.query(Task).filter(Task.user_id == current_user)
    
    # Apply completion filter
    if completed is not None:
        query = query.filter(Task.completed == completed)
        logger.info(f"Applying completion filter: {completed}")
    
    # Apply search filter
    if search:
        query = query.filter(or_(Task.title.contains(search), Task.description.contains(search)))
        logger.info(f"Applying search filter: {search}")
    
    # Apply sorting
    if sort_by == "created_at":
        if sort_order == "asc":
            query = query.order_by(Task.created_at.asc())
        else:
            query = query.order_by(Task.created_at.desc())
    elif sort_by == "updated_at":
        if sort_order == "asc":
            query = query.order_by(Task.updated_at.asc())
        else:
            query = query.order_by(Task.updated_at.desc())
    elif sort_by == "title":
        if sort_order == "asc":
            query = query.order_by(Task.title.asc())
        else:
            query = query.order_by(Task.title.desc())
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    tasks = query.all()
    logger.info(f"Retrieved {len(tasks)} tasks for user {current_user}")
    return tasks


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_task(
    request: Request,
    task_data: TaskCreate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.
    """
    logger.info(f"Creating task for user {current_user}")

    # Create task with the authenticated user's ID
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=task_data.completed,
        priority=task_data.priority,  # Include priority
        due_date=task_data.due_date,  # Include due date
        user_id=current_user,
        last_modified_by=current_user
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    logger.info(f"Task {db_task.id} created successfully for user {current_user}")
    return TaskRead(
        id=db_task.id,
        user_id=db_task.user_id,
        title=db_task.title,
        description=db_task.description,
        completed=db_task.completed,
        priority=db_task.priority,  # Include priority in response
        due_date=db_task.due_date,  # Include due date in response
        created_at=db_task.created_at,
        updated_at=db_task.updated_at,
        last_modified_by=db_task.last_modified_by
    )


@router.get("/{task_id}", response_model=TaskRead)
@limiter.limit("20/minute")
def read_task(
    request: Request,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific task by ID.
    """
    logger.info(f"Fetching task {task_id} for user {current_user}")
    
    task = session.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        logger.warning(f"Task {task_id} not found for user {current_user}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify that the task belongs to the current user
    if task.user_id != current_user:
        logger.warning(f"Access denied: User {current_user} tried to access task {task_id} belonging to user {task.user_id}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    logger.info(f"Task {task_id} retrieved successfully for user {current_user}")
    return TaskRead(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=task.priority,  # Include priority in response
        due_date=task.due_date,  # Include due date in response
        created_at=task.created_at,
        updated_at=task.updated_at,
        last_modified_by=task.last_modified_by
    )


@router.put("/{task_id}", response_model=TaskRead)
@limiter.limit("10/minute")
def update_task(
    request: Request,
    task_id: int,
    task_update: TaskUpdate,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task by ID.
    """
    logger.info(f"Updating task {task_id} for user {current_user}")

    db_task = session.query(Task).filter(and_(Task.id == task_id, Task.user_id == current_user)).first()

    if not db_task:
        logger.warning(f"Task {task_id} not found for user {current_user}")
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the current user
    if db_task.user_id != current_user:
        logger.warning(f"Access denied: User {current_user} tried to update task {task_id} belonging to user {db_task.user_id}")
        raise HTTPException(status_code=403, detail="Access denied")

    # Update the task with the provided values
    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.completed is not None:
        db_task.completed = task_update.completed
    if task_update.priority is not None:
        db_task.priority = task_update.priority
    if task_update.due_date is not None:
        db_task.due_date = task_update.due_date

    db_task.updated_at = datetime.utcnow()
    db_task.last_modified_by = current_user
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    logger.info(f"Task {task_id} updated successfully for user {current_user}")
    return TaskRead(
        id=db_task.id,
        user_id=db_task.user_id,
        title=db_task.title,
        description=db_task.description,
        completed=db_task.completed,
        priority=db_task.priority,  # Include priority in response
        due_date=db_task.due_date,  # Include due date in response
        created_at=db_task.created_at,
        updated_at=db_task.updated_at,
        last_modified_by=db_task.last_modified_by
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def delete_task(
    request: Request,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task by ID.
    """
    logger.info(f"Deleting task {task_id} for user {current_user}")
    
    task = session.query(Task).filter(and_(Task.id == task_id, Task.user_id == current_user)).first()
    
    if not task:
        logger.warning(f"Task {task_id} not found for user {current_user}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify that the task belongs to the current user
    if task.user_id != current_user:
        logger.warning(f"Access denied: User {current_user} tried to delete task {task_id} belonging to user {task.user_id}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    session.delete(task)
    session.commit()
    
    logger.info(f"Task {task_id} deleted successfully for user {current_user}")
    return


@router.patch("/{task_id}/complete", response_model=TaskRead)
@limiter.limit("10/minute")
def toggle_task_completion(
    request: Request,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a task.
    """
    logger.info(f"Toggling completion status for task {task_id} for user {current_user}")
    
    task = session.query(Task).filter(and_(Task.id == task_id, Task.user_id == current_user)).first()
    
    if not task:
        logger.warning(f"Task {task_id} not found for user {current_user}")
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify that the task belongs to the current user
    if task.user_id != current_user:
        logger.warning(f"Access denied: User {current_user} tried to toggle completion for task {task_id} belonging to user {task.user_id}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Toggle the completion status
    old_status = task.completed
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    task.last_modified_by = current_user
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    logger.info(f"Task {task_id} completion status toggled from {old_status} to {task.completed} for user {current_user}")
    return TaskRead(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=task.priority,  # Include priority in response
        due_date=task.due_date,  # Include due date in response
        created_at=task.created_at,
        updated_at=task.updated_at,
        last_modified_by=task.last_modified_by
    )