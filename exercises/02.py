# Ćwiczenie 3: Pydantic Schemas - Walidacja i Serializacja
#
# ZADANIE:
# CRUD jest już gotowy, ale brakuje walidacji Pydantic!
# Twoim zadaniem jest dodać schematy Pydantic i walidację do wszystkich endpointów.
#
# TODO (krok po kroku):
# 1. Stwórz Enum TaskPriority z wartościami: low, medium, high
# 2. Stwórz Enum TaskStatus z wartościami: todo, in_progress, done
# 3. Stwórz schema TaskCreate z polami:
#    - title: str (min 3, max 100 znaków)
#    - description: Optional[str] (max 500 znaków jeśli podane)
#    - priority: TaskPriority (domyślnie: medium)
#    - status: TaskStatus (domyślnie: todo)
#    - due_date: Optional[str] (format YYYY-MM-DD, użyj pattern `r'^\d{4}-\d{2}-\d{2}$` w Field)
# 4. Stwórz schema TaskUpdate (identyczny jak TaskCreate)
# 5. Stwórz schema TaskResponse z polami:
#    - id: int
#    - title: str
#    - description: Optional[str]
#    - priority: TaskPriority
#    - status: TaskStatus
#    - due_date: Optional[str]
# 6. Użyj TaskCreate w POST /tasks (zamień Body() na TaskCreate)
# 7. Użyj TaskUpdate w PUT /tasks/{task_id} (zamień Body() na TaskUpdate)
# 8. Dodaj response_model=TaskResponse do wszystkich endpointów (poza DELETE)
# 9. W GET /tasks zwracaj {"tasks": [...], "count": ...} z TaskResponse dla każdego taska
#
# BONUS (opcjonalnie):
# 10. Dodaj custom validator do due_date sprawdzający czy data nie jest w przeszłości

from fastapi import FastAPI, HTTPException, Response, Body, status
from typing import Optional

app = FastAPI(title="Task Management API")

# TODO: Dodaj importy dla Pydantic
# from pydantic import BaseModel, Field
# from enum import Enum

# TODO: Stwórz Enum TaskPriority (low, medium, high)

# TODO: Stwórz Enum TaskStatus (todo, in_progress, done)

# TODO: Stwórz schema TaskCreate

# TODO: Stwórz schema TaskUpdate

# TODO: Stwórz schema TaskResponse


# Mock database - przykładowe dane
tasks_db = {
    1: {
        "id": 1,
        "title": "Napisz testy jednostkowe",
        "description": "Dodać testy dla modułu auth",
        "priority": "high",
        "status": "in_progress",
        "due_date": "2026-06-20"
    },
    2: {
        "id": 2,
        "title": "Code review PR#123",
        "description": None,
        "priority": "medium",
        "status": "todo",
        "due_date": None
    },
}
next_id = 3


# TODO: Dodaj response_model=TaskResponse
@app.post("/tasks", status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(
    # TODO: Zamień na: task: TaskCreate
    title: str = Body(),
    description: Optional[str] = Body(None),
    priority: str = Body("medium"),
    status: str = Body("todo"),
    due_date: Optional[str] = Body(None)
):
    """Stwórz nowe zadanie"""
    global next_id

    new_task = {
        "id": next_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "due_date": due_date,
    }

    tasks_db[next_id] = new_task
    next_id += 1

    return new_task


@app.get("/tasks", status_code=status.HTTP_200_OK, tags=["tasks"])
def get_tasks():
    """
    Pobierz listę zadań

    TODO: Zwracane taski powinny być walidowane przez TaskResponse
    """
    tasks = list(tasks_db.values())
    return {"tasks": tasks, "count": len(tasks)}


# TODO: Dodaj response_model=TaskResponse
@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK, tags=["tasks"])
def get_task(task_id: int):
    """Pobierz pojedyncze zadanie"""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return tasks_db[task_id]


# TODO: Dodaj response_model=TaskResponse
@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK, tags=["tasks"])
def update_task(
    task_id: int,
    # TODO: Zamień na: task: TaskUpdate
    title: str = Body(),
    description: Optional[str] = Body(None),
    priority: str = Body("medium"),
    status: str = Body("todo"),
    due_date: Optional[str] = Body(None)
):
    """Zaktualizuj zadanie"""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Aktualizacja wszystkich pól
    tasks_db[task_id]["title"] = title
    tasks_db[task_id]["description"] = description
    tasks_db[task_id]["priority"] = priority
    tasks_db[task_id]["status"] = status
    tasks_db[task_id]["due_date"] = due_date

    return tasks_db[task_id]


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int):
    """Usuń zadanie"""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    del tasks_db[task_id]

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# TESTOWANIE:
# 1. Uruchom: uvicorn 02:app --reload
# 2. Otwórz: http://localhost:8000/docs
# 3. Sprawdź czy:
#    - Swagger pokazuje poprawne schematy
#    - Walidacja działa (spróbuj wysłać title z 1 znakiem)
#    - Enum pokazuje się jako dropdown
#    - Pattern dla due_date jest sprawdzany
#    - Response filtruje pola (jeśli zwracasz dict z dodatkowymi polami)