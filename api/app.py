import datetime
import json
import uuid
from typing import Dict, Any

from db.db_store import AsyncSessionLocal
from crud.session import get_session_by_id, save_session
from crud.messages import save_message, get_message
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse
from fastapi import APIRouter, Depends
from tools.logger import logger
from crud.messages import save_message
from crud.session import get_sessions, save_session, get_session_by_id
from db import db_store
from model.Request import RequestData
from tools.graph_store import graph, get_graph
from tools.is_allowed import is_allowed
from model.ApiResponse import success,fail
app_router = APIRouter(prefix="/api/chat",tags=["会话"])


@app_router.post("/dialogue",summary="进行会话")
async def dialogue(request: RequestData):
    if request.session_id == "":
        return fail("session_id不能为空")
    if request.question == "":
        return fail("内容不能为空")
    if not is_allowed(request.session_id):
        return fail("请求次数过多,请稍后再试")
    try:
        # 获取完整的响应
        result = await generate_response(request.session_id, request.question)
        return success(result)
    except Exception as e:
        logger.error(f"对话处理失败: {e}")
        return fail(f"处理失败: {str(e)}")

@app_router.get("/get_sessions",summary="查询历史会话")
async def get_sessions_list(skip=0,limit:int=10,db = Depends(db_store.get_db)):
    sessions = await get_sessions(db,skip,limit)
    return success(sessions)

@app_router.get("/get_session/{session_id}",summary="根据会话id查询会话内容")
async def get_session(session_id:str,db = Depends(db_store.get_db)):
    messages = await get_message(db,session_id)
    return success(messages)
@app_router.get("/add_session",summary="创建会话")
async def add_session(db = Depends(db_store.get_db)):
    session_id = f"session:{str(uuid.uuid4())}"
    await save_session(db, session_id, create_session_title())
    return success(session_id)


async def generate_response(session_id: str, question: str) -> Dict[str, Any]:
    """生成完整响应，不再流式"""
    logger.info(f"开始处理问题: {question}")

    graph = await get_graph()

    try:
        # ✅ 关键修复：用 ainvoke 一次性获取结果，不再流式
        final_state = await graph.ainvoke({
            "input": question,
            "session_id": session_id
        })
        logger.info(f"final_state: {final_state}")
        # ✅ 【修复完成】正确取出 result 字典
        result = final_state.get("result", {})

        company = result.get("company", "")
        industry = result.get("industry", "")
        final_analysis = result.get("analysis", "")
        score = result.get("score", 0)
        recommendation = result.get("recommendation", "")

    except Exception as e:
        logger.error(f"处理图流失败: {e}")
        raise Exception(f"AI处理失败: {str(e)}")

    # ✅ 【修复完成】清洗空白字符 + 正确判断逻辑
    company_clean = company.strip()
    industry_clean = industry.strip()

    # 闲聊
    if (company_clean in ["未提供", "", "无"]) and (industry_clean in ["未提供", "", "无"]):
        result_data = {
            "type": "chat",
            "content": final_analysis
        }
    else:
        result_data = {
            "type": "analysis",
            "data": {
                "company": company_clean,
                "industry": industry_clean,
                "analysis": final_analysis,
                "score": score,
                "recommendation": recommendation
            }
        }

    # 保存数据库
    try:
        async with AsyncSessionLocal() as tmp_db:
            session = await get_session_by_id(tmp_db, session_id)
            if not session:
                await save_session(tmp_db, session_id, create_session_title())

            await save_message(tmp_db, session_id, "user", question)
            if final_analysis:
                await save_message(tmp_db, session_id, "assistant", json.dumps(result_data, ensure_ascii=False))
    except Exception as e:
        logger.error(f"保存消息到数据库失败: {e}")

    logger.info(f"处理完成，结果类型: {result_data.get('type')}")
    return result_data

def create_session_title()->str:
    return f"会话：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"