"""Task CRUD endpoints - API v1."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from dependencies import DbSession, PositiveInt, AdminUser
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse


router = APIRouter(prefix="/tasks", tags=["Tasks"])


# C (Create)
@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
def create_task(task: TaskCreate, db: DbSession):
    """Create a new task."""
    db_task = Task(name=task.name)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# R (Read all)
@router.get("", response_model=dict)
def get_tasks(db: DbSession):
    """Get all tasks."""
    stmt = select(Task)
    tasks = db.execute(stmt).scalars().all()
    tasks_list = [{"id": task.id, "name": task.name} for task in tasks]
    return {"tasks": tasks_list, "count": len(tasks_list)}


# R (Read detail)
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: PositiveInt, db: DbSession):
    """Get a single task by ID."""
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task


# U (Update)
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: PositiveInt, task: TaskUpdate, db: DbSession):
    """Update a task."""
    db_task = db.get(Task, task_id)

    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    db_task.name = task.name
    db.commit()
    db.refresh(db_task)
    return db_task


# D (Delete) - REQUIRES ADMIN ROLE
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: PositiveInt, db: DbSession, admin_user: AdminUser):
    """Delete a task (requires admin role - authorization)."""
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
