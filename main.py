from datetime import datetime
from uuid import uuid1
from fastapi import FastAPI
from passlib.hash import pbkdf2_sha256
from pydantic import BaseModel, Field
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.fastapi import register_tortoise
from typing import List


class User(Model):
    id = fields.IntField(pk=True)
    user_name = fields.CharField(50, unique=True)
    password = fields.CharField(150)
    first_name = fields.CharField(50)
    last_name = fields.CharField(50)
    gender = fields.CharField(1)
    create_at = fields.CharField(50)
    status = fields.CharField(1)
    salt = fields.BinaryField()


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
    salt = str(uuid1()).encode()
    date = datetime.now()
    user = await User.create(
        user_name=user.user_name,
        password=pbkdf2_sha256.using(salt=salt).hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        create_at=date,
        status="1",
        salt=salt
    )
    return await UserList.from_tortoise_orm(user)


@app.get("/login/{user_name}/{password}")
async def login_user(user_name: str, password: str):
    user_from_db = await User.get(user_name=user_name)
    is_auth = user_from_db.password == pbkdf2_sha256.using(salt=user_from_db.salt).hash(password)
    return {"is_auth": is_auth}


register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)
