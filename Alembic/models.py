from fastapi import HTTPException, status
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class UsersModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String)
    address_id = Column(Integer, ForeignKey("address.id"), nullable=True)

    todos = relationship("TodosModel", back_populates="owner")
    address = relationship("AddressModel", back_populates="user_address")


class TodosModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("UsersModel", back_populates="todos")


class AddressModel(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postalcode = Column(String)

    apt_num = Column(Integer)

    user_address = relationship("UsersModel", back_populates="address")


class ModuleException(HTTPException):
    def __init__(self, function_name: str, message: str, status_code: int = None,
                 headers: dict = None):
        self.detail = '{}: {}'.format(function_name, message)
        if status_code is not None:
            self.status_code = status_code
        if headers is not None:
            self.headers = headers
        else:
            self.headers = self.detail


class UserAlreadyExistsException(ModuleException):
    def __init__(self, function_name, username, headers : dict = None):
        super().__init__(function_name,
                         message='The User [{}] already exists.'.format(username),
                         status_code=status.HTTP_409_CONFLICT,
                         headers=headers)


class EmailAlreadyExistsException(ModuleException):
    def __init__(self, function_name, email, headers : dict = None):
        super().__init__(function_name,
                         message='The email [{}] already exists.'.format(email),
                         status_code=status.HTTP_409_CONFLICT,
                         headers=headers)



'''
=========================================================================
'''

'''
from fastapi import HTTPException, status
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class UsersModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    todos = relationship("TodosModel", back_populates="owner")


class TodosModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("UsersModel", back_populates="todos")

'''







