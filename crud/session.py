from sqlalchemy import Select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from crud.messages import remove_messages
from db.models import ChatSession, ChatMessage


async def get_sessions(db:AsyncSession,skip:int =0,limit:int = 10):
    """
    :param db: 数据库
    :param skip: 跳过页数
    :param limit: 当前条数
    :return:
    """
    sessions = await db.execute(Select(ChatSession).offset(skip*limit).limit(limit))
    return sessions.scalars().all()

async def save_session(db:AsyncSession,session_id:str,title:str):
    """
    :param db:
    :param session_id:
    :param title:标题
    :return:
    """
    session = ChatSession(session_id=session_id,title=title)
    db.add(session)
    await db.commit()

async def remove_session(db:AsyncSession,session_id:str):
    """
    :param db:
    :param session_id:
    :return:
    """
    session = await db.execute(Select(ChatSession).where(ChatSession.session_id==session_id))
    s = session.scalar_one_or_none()
    await db.delete(s)
    await remove_messages(db,session_id)
    await db.commit()

async def get_session_by_id(db:AsyncSession,session_id):
    """
    :param session_id:
    :param db: 数据库
    :return:
    """
    sessions = await db.execute(Select(ChatSession).where(ChatSession.session_id==session_id))
    return sessions.scalar_one_or_none()