import inspect
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from auth import get_current_user
from database import SessionLocal, engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = Field(min_length=1, max_length=100, default=None)
    description: Optional[str] = Field(min_length=1, max_length=100)
    complete: Optional[bool] = False
    priority: Optional[int] = Field(
        ge=1, le=5, description="1 is lowest priority, 5 is highest priority", default=1)

    class Config:
        schema_extra = {
            "example": {
                "title": "Take a nap",
                "description": "Take a nap for 30 minutes",
                "complete": False,
                "priority": 1
            }
        }

# CRUDS methods


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise models.ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found", status_code=status.HTTP_404_NOT_FOUND)

    return db.query(models.Todos)\
        .filter(models.Todos.owner_id == user["id"])\
        .all()


@app.get("/todos/user", status_code=status.HTTP_200_OK)
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise models.ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found", status_code=status.HTTP_404_NOT_FOUND)

    return db.query(models.Todos)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(todo_id: int,
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user is None:
        raise models.ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()
    if todo_model is not None:
        return todo_model
    raise http_exception(todo_id=todo_id)


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise models.ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    todo_model = models.Todos(title=todo.title,
                              description=todo.description,
                              complete=todo.complete,
                              priority=todo.priority,
                              owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return {
        "message": "Todo created successfully",
        'inserted_record': todo_model,
    }


@app.put("/todo/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_todo(todo_id: int, todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise models.ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()

    if todo_model is not None:
        if todo.title:
            todo_model.title = todo.title
        if todo.description:
            todo_model.description = todo.description
        if todo.complete:
            todo_model.complete = todo.complete
        if todo.priority:
            todo_model.priority = todo.priority

        db.commit()
        db.refresh(todo_model)

        return {
            "message": 'Todo with id [{}] updated successfully'.format(todo_id),
            'updated_record': todo_model,
        }
    raise http_exception(todo_id=todo_id)


@app.delete("/todo/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_todo(todo_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise models.ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    todo_model = db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .first()

    if todo_model is not None:
        db.delete(todo_model)

        db.commit()

        return {
            "message": 'Todo with id [{}] deleted successfully'.format(todo_id),
        }

    raise http_exception(todo_id=todo_id)

# EXTRAS


def http_exception(todo_id: int = None):
    if todo_id is not None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"Todo with id [{todo_id}] not found")
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="Todo not found")
