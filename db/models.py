from sqlalchemy import Column, String, Text, TIMESTAMP, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    session_id = Column(String(64), primary_key=True)
    title = Column(String(255))
    # 给默认值，插入时自动生成时间
    create_time = Column(TIMESTAMP, default=datetime.now)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    # id 改为自增整数
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64))
    role = Column(String(16))
    content = Column(Text)
    create_time = Column(TIMESTAMP, default=datetime.now)