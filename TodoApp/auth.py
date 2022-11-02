import inspect
from datetime import datetime, timedelta
from typing import Optional

#from fastapi import Depends, FastAPI, Request, status
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib import context
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from database import SessionLocal, engine
from models import (Base, EmailAlreadyExistsException, ModuleException, Todos,
                    UserAlreadyExistsException, Users)

SECRET_KEY = "a0d3b0e1c0d0b0e1c0d0b0e1c0d0b0e1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class CreateUser(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: Optional[str] = Field(min_length=1, max_length=50)
    first_name: Optional[str] = Field(min_length=1, max_length=50)
    last_name: Optional[str] = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=50)

    class Config:
        schema_extra = {
            "example": {
                "username": "john",
                "email": "joedoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "test1234!"
            }
        }


bcrypt_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

#app = FastAPI()
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password: str):
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    to_encode = {
        "sub": username,
        "id": user_id
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# CRUD methods

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        
        if username is None or user_id is None:
            raise ModuleException(
                inspect.currentframe().f_code.co_name,
                message='User [{}] not found.'.format(username),
                status_code=status.HTTP_404_NOT_FOUND
            )

        return {"username": username, "id": user_id}

    except JWTError:
        raise ModuleException(
            inspect.currentframe().f_code.co_name,
            message="Could not validate credentials in JWT: {}".format(JWTError.message),
            status_code=status.HTTP_404_NOT_FOUND
        )

#@app.post("/create/user", status_code=status.HTTP_201_CREATED)
@router.post("/create/user", status_code=status.HTTP_201_CREATED)
async def create_new_user(user: CreateUser, db: Session = Depends(get_db)):
    try:
        create_user_model = Users(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=get_password_hash(user.password),
            is_active=True
        )

        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)

        return create_user_model

    except Exception as e:
        raise ModuleException(
            inspect.currentframe().f_code.co_name,
            message='DBERROR: username=[{}] | email=[{}]: {}'.format(
                user.username, user.email, e.args[0]),
            status_code=status.HTTP_400_BAD_REQUEST
        )

#@app.post("/token")
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise ModuleException(
            inspect.currentframe().f_code.co_name,
            message='Incorrect username or password.',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        username=user.username, user_id=user.id, expires_delta=access_token_expires)

    return {"token": access_token, "token_type": "bearer"}

# EXCEPTIONS

@app.exception_handler(ModuleException)
async def module_exception_handler(request: Request, exc: ModuleException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
        headers={"X-Header-Error": exc.headers}
    )

