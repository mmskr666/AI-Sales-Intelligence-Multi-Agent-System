import datetime

from pydantic import BaseModel


class ChatMessages(BaseModel):
    id:int
    session_id:str
    role:str
    content:str
