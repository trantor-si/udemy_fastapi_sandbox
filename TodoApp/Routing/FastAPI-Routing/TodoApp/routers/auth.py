import inspect
import sys

sys.path.append("..")

from datetime import datetime, timedelta
from typing import Optional

from database import SessionLocal, engine
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models import Base, ModuleException, UsersModel
from passlib import context
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

SECRET_KEY = "a0d3b0e1c0d0b0e1c0d0b0e1c0d0b0e1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


bcrypt_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(bind=engine)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

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
    user_model = db.query(UsersModel).filter(UsersModel.username == username).first()
    if not user_model:
        return False
    if not verify_password(password, user_model.hashed_password):
        return False
    return user_model


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

# @router.exception_handler(ModuleException)
# async def module_exception_handler(request: Request, exc: ModuleException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": exc.detail},
#         headers={"X-Header-Error": exc.headers}
#     )

