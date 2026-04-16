from sqlalchemy import insert,Select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import ChatMessage


async def save_message(db:AsyncSession,session_id:str,role:str,content:str):
    await db.execute(insert(ChatMessage).values(session_id=session_id,role=role,content=content))
    await db.commit()

async def get_message(db:AsyncSession,session_id:str):
    messages = await db.execute(Select(ChatMessage).where(ChatMessage.session_id==session_id))
    return messages.scalars().all()

async def remove_messages(db:AsyncSession,session_id:str):
    """
    :param db:
    :param session_id:
    :return:
    """
    await db.execute(
        delete(ChatMessage).where(ChatMessage.session_id == session_id)
    )
