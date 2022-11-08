import sys

sys.path.append("..")

from typing import Optional

from database import SessionLocal, engine
from fastapi import APIRouter, Depends, status
from models import AddressModel, Base, ModuleException, UsersModel
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/address",
    tags=["address"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Address Not found"}},
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Address(BaseModel):
    address1: str = Field(min_length=1, max_length=200)
    address2: Optional[str] = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=50)
    state: str = Field(min_length=1, max_length=50)
    country: str = Field(min_length=1, max_length=50)
    postalcode: str = Field(min_length=1, max_length=20)

    apt_num: Optional[int]

    class Config:
        schema_extra = {
            "example": {
                "address1": "One street",
                "address2": "501 / 1",
                "city": "One city",
                "state": "One State",
                "country": "One Country",
                "postalcode": "12345-678",
                "apt_num": 501
            }
        }

# CRUD methods

@router.post("/")
async def create_address(address: Address,
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    address_model = AddressModel()
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode
    address_model.apt_num = address.apt_num

    db.add(address_model)
    db.flush()
    db.refresh(address_model)

    user_model = db.query(UsersModel).filter(UsersModel.id == user.get("id")).first()
    user_model.address_id = address_model.id

    db.add(user_model)
    db.commit()

    return {
        'message': 'Address created successfully for user: [{}].'.format(user.get("username")),
        'inserted_record': address_model,
    }








