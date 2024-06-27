from fastapi import FastAPI
from pydantic import BaseModel
from libs.database import Account


class user_data(BaseModel):
    user_id: str
    user_password: str


app = FastAPI()

Account = Account(db_name='game_bot.db')


@app.post("/v1/login")
async def login_user(data: user_data):
    return Account.user_login(user_id=data.user_id, user_password=data.user_password)


@app.post("/v1/delete")
async def delete_user(data: user_data):
    return Account.delete_user(user_id=data.user_id, user_password=data.user_password)
