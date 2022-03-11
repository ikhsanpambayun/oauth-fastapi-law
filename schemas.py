from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    username: str
    hashed_password: str
    full_name: str
    npm: str
    client_id: str
    client_secret: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    id: int
    access_token: str
    timestamp: datetime
    owner_username: str

    class Config:
        orm_mode = True