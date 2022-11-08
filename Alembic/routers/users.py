import inspect
import sys
from typing import Optional

import models
from database import SessionLocal, engine
from fastapi import APIRouter, Depends, HTTPException, status
from models import Base, ModuleException, UsersModel
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .auth import get_current_user, get_password_hash

sys.path.append("..")


class User(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: Optional[str] = Field(min_length=1, max_length=50)
    first_name: Optional[str] = Field(min_length=1, max_length=50)
    last_name: Optional[str] = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=50)
    
    phone_number: Optional[str] = Field(min_length=1, max_length=50)

    class Config:
        schema_extra = {
            "example": {
                "username": "john",
                "email": "joedoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "test1234!",
                "phone_number": "1234567890"
            }
        }


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# CRUD methods


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: Session = Depends(get_db)):
    return db.query(UsersModel).all()


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user_id: int,
                    db: Session = Depends(get_db)):
    user_model = db.query(UsersModel)\
        .filter(UsersModel.id == user_id)\
        .first()
    if user_model is not None:
        return user_model
    raise http_exception(todo_id=user_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_user(user: User, db: Session = Depends(get_db)):
    try:
        user_model = UsersModel(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=get_password_hash(user.password),
            is_active=True,

            phone_number=user.phone_number
        )

        db.add(user_model)
        db.commit()
        db.refresh(user_model)

        return user_model

    except Exception as e:
        raise ModuleException(
            inspect.currentframe().f_code.co_name,
            message='DBERROR: username=[{}] | email=[{}]: {}'.format(
                user.username, user.email, e.args[0]),
            status_code=status.HTTP_400_BAD_REQUEST
        )


@router.put("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_user(user_id: int, user: User,
                      db: Session = Depends(get_db)):
    if user is None:
        raise models.ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found.", status_code=status.HTTP_404_NOT_FOUND)

    user_model = db.query(UsersModel)\
        .filter(UsersModel.id == user_id)\
        .first()

    if user_model is not None:
        if user.username is not None:
            user_model.username = user.username
        if user.email is not None:
            user_model.email = user.email
        if user.first_name is not None:
            user_model.first_name = user.first_name
        if user.last_name is not None:
            user_model.last_name = user.last_name
        if user.is_active is not None:
            user_model.is_active = user.is_active
        if user.phone_number is not None:
            user_model.phone_number = user.phone_number

        db.commit()
        db.refresh(user_model)

        return {
            "message": 'User with id [{}] updated successfully'.format(user_id),
            'updated_record': user_model,
        }
    raise http_exception(todo_id=user_id)


@router.put("/password/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_password(user_id: int, new_password: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found", status_code=status.HTTP_404_NOT_FOUND)

    user_model = db.query(UsersModel)\
        .filter(UsersModel.id == user_id)\
        .first()

    if user_model is not None:
        if user.password is not None:
            user_model.hashed_password = get_password_hash(user.password)

        db.commit()
        db.refresh(user_model)

        return {
            "message": 'User with id [{}] updated successfully'.format(user_id),
            'updated_record': user_model,
        }

    raise http_exception(todo_id=user_id)


@router.delete("/", status_code=status.HTTP_202_ACCEPTED)
async def delete_todo(user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise ModuleException(
            function_name=inspect.currentframe().f_code.co_name,
            message="User not found", status_code=status.HTTP_404_NOT_FOUND)

    user_id = user['id']
    user_model = db.query(UsersModel)\
        .filter(UsersModel.id == user_id)\
        .first()

    if user_model is not None:
        db.delete(user_model)
        db.commit()

        return {
            "message": 'User with id [{}] deleted successfully'.format(user_id),
        }

    raise http_exception(todo_id=user_id)

# EXTRAS


def http_exception(user_id: int = None):
    if user_id is not None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"User with id [{user_id}] not found")
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                         detail="User not found")
