import datetime

from pydantic import BaseModel


class ChatSession(BaseModel):
    session_id: str
    title: str
