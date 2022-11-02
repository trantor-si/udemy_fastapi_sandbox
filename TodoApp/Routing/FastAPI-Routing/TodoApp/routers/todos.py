import inspect
import sys

sys.path.append("..")

from typing import Optional

from database import SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException, status
from models import Base, ModuleException, TodosModel
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .auth import get_current_user

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

Base.metadata.create_all(bind=engine)

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
    priority: Optional[int] = Field(
        ge=1, le=5, description="1 is lowest priority, 5 is highest priority", default=1)
    complete: Optional[bool] = False

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


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found", status_code=status.HTTP_404_NOT_FOUND)

    return db.query(TodosModel)\
        .filter(TodosModel.owner_id == user["id"])\
        .all()


@router.get("/user", status_code=status.HTTP_200_OK)
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found", status_code=status.HTTP_404_NOT_FOUND)

    return db.query(TodosModel)\
        .filter(TodosModel.owner_id == user.get("id"))\
        .all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(todo_id: int,
                    user: dict = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if user is None:
        raise ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    todo_model = db.query(TodosModel)\
        .filter(TodosModel.id == todo_id)\
        .filter(TodosModel.owner_id == user.get("id"))\
        .first()
    if todo_model is not None:
        return todo_model
    raise http_exception(todo_id=todo_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    todo_model = TodosModel(title=todo.title,
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


@router.put("/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_todo(todo_id: int, todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    todo_model = db.query(TodosModel)\
        .filter(TodosModel.id == todo_id)\
        .filter(TodosModel.owner_id == user.get("id"))\
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


@router.delete("/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_todo(todo_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    todo_model = db.query(TodosModel)\
        .filter(TodosModel.id == todo_id)\
        .filter(TodosModel.owner_id == user.get("id"))\
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
