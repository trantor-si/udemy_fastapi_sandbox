from fastapi import Depends, FastAPI

import models
from company import companyapis, dependencies
from database import engine
from routers import address, auth, todos, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(address.router)
app.include_router(users.router)
app.include_router(
    companyapis.router,
    prefix="/companyapis",
    tags=["companysapis"],
    dependencies=[Depends(dependencies.get_token_header)],
    responses={418: {"description": "Internal Use Only"}}
)
