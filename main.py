from datetime import datetime
from uuid import uuid1

from fastapi import FastAPI
from pydantic import BaseModel, Field
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.fastapi import register_tortoise
from typing import List


class User(Model):
    id = fields.CharField(50, pk=True)
    user_name = fields.CharField(50, unique=True)
    password = fields.CharField(50)
    first_name = fields.CharField(50)
    last_name = fields.CharField(50)
    gender = fields.CharField(1)
    create_at = fields.CharField(50)
    status = fields.CharField(1)


UserList = pydantic_model_creator(User, name="User")


class UserEntry(BaseModel):
    user_name: str = Field(..., example="Lena_user_name")
    password: str = Field(..., example="password 123")
    first_name: str = Field(..., example="Lena")
    last_name: str = Field(..., example="Bogdanovna")
    gender: str = Field(..., example="M")


app = FastAPI()


@app.get("/users", response_model=List[UserList])
async def find_all_users():
    all_query = await UserList.from_queryset(User.all())
    return list(all_query)


@app.post("/users", response_model=UserList)
async def register_user(user: UserEntry):
    gTD = str(uuid1())
    gDate = datetime.now()
    user = await User.create(
        id=gTD,
        user_name=user.user_name,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        create_at=gDate,
        status="1"
    )
    return await UserList.from_tortoise_orm(user)


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)
