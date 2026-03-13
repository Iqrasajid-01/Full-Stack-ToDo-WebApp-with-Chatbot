"""
MCP Tools for Task Operations
These functions implement the core task operations for the MCP server.
"""

import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.task import TaskCreate, TaskUpdate, TaskRead, TaskDB as Task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_task_tool(user_id: str, task_data: TaskCreate, session: Session) -> TaskRead:
    """
    Add a new task to the user's todo list.

    Args:
        user_id: The ID of the user creating the task
        task_data: The task data to create
        session: Database session

    Returns:
        Created task as TaskRead object
    """
    try:
        logger.info(f"Adding task for user {user_id}: {task_data.title}")

        # Create task with the authenticated user's ID
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            priority=task_data.priority,
            due_date=task_data.due_date,
            user_id=user_id,
            last_modified_by=user_id
        )

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        logger.info(f"Task {db_task.id} created successfully for user {user_id}")

        return TaskRead(
            id=db_task.id,
            user_id=db_task.user_id,
            title=db_task.title,
            description=db_task.description,
            completed=db_task.completed,
            priority=db_task.priority,
            due_date=db_task.due_date,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            last_modified_by=db_task.last_modified_by
        )
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error in add_task_tool: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in add_task_tool: {str(e)}")
        raise


async def list_tasks_tool(user_id: str, completed: Optional[bool] = None,
                         limit: int = 50, skip: int = 0, session: Session = None) -> List[TaskRead]:
    """
    List tasks from the user's todo list.

    Args:
        user_id: The ID of the user whose tasks to list
        completed: Filter by completion status (None for all, True for completed, False for incomplete)
        limit: Maximum number of records to return
        skip: Number of records to skip
        session: Database session

    Returns:
        List of tasks as TaskRead objects
    """
    try:
        logger.info(f"Listing tasks for user {user_id}, completed={completed}")

        # Build the query with filters
        query = session.query(Task).filter(Task.user_id == user_id)

        # Apply completion filter
        if completed is not None:
            query = query.filter(Task.completed == completed)
            logger.debug(f"Applied completion filter: {completed}")

        # Apply sorting and pagination
        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)

        tasks = query.all()
        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")

        # Convert to TaskRead objects
        task_reads = []
        for task in tasks:
            task_read = TaskRead(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                completed=task.completed,
                priority=task.priority,
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at,
                last_modified_by=task.last_modified_by
            )
            task_reads.append(task_read)

        return task_reads
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_tasks_tool: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in list_tasks_tool: {str(e)}")
        raise


async def complete_task_tool(user_id: str, task_id: int, completed: bool,
                           session: Session) -> TaskRead:
    """
    Complete or uncomplete a task.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        completed: Whether the task should be marked as completed
        session: Database session

    Returns:
        Updated task as TaskRead object
    """
    try:
        logger.info(f"Updating completion status for task {task_id} for user {user_id}, completed={completed}")

        # Find the task
        db_task = session.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        # Update the completion status
        old_status = db_task.completed
        db_task.completed = completed
        db_task.updated_at = datetime.utcnow()
        db_task.last_modified_by = user_id

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        logger.info(f"Task {task_id} completion status updated from {old_status} to {completed} for user {user_id}")

        return TaskRead(
            id=db_task.id,
            user_id=db_task.user_id,
            title=db_task.title,
            description=db_task.description,
            completed=db_task.completed,
            priority=db_task.priority,
            due_date=db_task.due_date,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            last_modified_by=db_task.last_modified_by
        )
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error in complete_task_tool: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in complete_task_tool: {str(e)}")
        raise


async def delete_task_tool(user_id: str, task_id: int, session: Session) -> bool:
    """
    Delete a task from the user's todo list.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to delete
        session: Database session

    Returns:
        True if task was deleted successfully
    """
    try:
        logger.info(f"Deleting task {task_id} for user {user_id}")

        # Find the task
        db_task = session.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        # Delete the task
        session.delete(db_task)
        session.commit()

        logger.info(f"Task {task_id} deleted successfully for user {user_id}")
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error in delete_task_tool: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in delete_task_tool: {str(e)}")
        raise


async def update_task_tool(user_id: str, task_id: int, task_update: TaskUpdate,
                          session: Session) -> TaskRead:
    """
    Update a task in the user's todo list.

    Args:
        user_id: The ID of the user
        task_id: The ID of the task to update
        task_update: The update data
        session: Database session

    Returns:
        Updated task as TaskRead object
    """
    try:
        logger.info(f"Updating task {task_id} for user {user_id}")

        # Find the task
        db_task = session.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if not db_task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise ValueError(f"Task {task_id} not found for user {user_id}")

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
        db_task.last_modified_by = user_id

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        logger.info(f"Task {task_id} updated successfully for user {user_id}")

        return TaskRead(
            id=db_task.id,
            user_id=db_task.user_id,
            title=db_task.title,
            description=db_task.description,
            completed=db_task.completed,
            priority=db_task.priority,
            due_date=db_task.due_date,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            last_modified_by=db_task.last_modified_by
        )
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error in update_task_tool: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in update_task_tool: {str(e)}")
        raise