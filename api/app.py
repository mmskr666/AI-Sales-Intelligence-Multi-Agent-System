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

    # 获取图实例
    graph = await get_graph()

    # 用来存最终的 analysis 文本
    all_chunks = []
    final_analysis = ""
    company = ""
    industry = ""
    score = 0
    recommendation = ""

    try:
        # 收集所有chunk
        async for chunk in graph.astream({
            "input": question,
            "session_id": session_id
        }):
            all_chunks.append(chunk)
            logger.debug(f"处理chunk: {chunk}")

            # 安全取出 result
            summary = chunk.get("summary", {})
            result = summary.get("result", {})

            # 提取各个字段
            chunk_company = result.get("company", "")
            chunk_industry = result.get("industry", "")
            chunk_analysis = result.get("analysis", "")
            chunk_score = result.get("score", 0)
            chunk_recommendation = result.get("recommendation", "")

            # 更新最终结果
            if chunk_company and chunk_company != "未提供":
                company = chunk_company
            if chunk_industry and chunk_industry != "未提供":
                industry = chunk_industry
            if chunk_analysis:
                final_analysis += chunk_analysis
            if chunk_score:
                score = chunk_score
            if chunk_recommendation:
                recommendation = chunk_recommendation

    except Exception as e:
        logger.error(f"处理图流失败: {e}")
        raise Exception(f"AI处理失败: {str(e)}")





    # 构建返回数据
    result_data = {}

    # 判断是自然闲聊还是公司分析
    if company in ["未提供", "", "无"] and industry in ["未提供", "", "无"]:
        # 自然闲聊，只返回analysis
        result_data = {
            "type": "chat",
            "content": final_analysis
        }
    else:
        # 公司分析，返回结构化数据
        result_data = {
            "type": "analysis",
            "data": {
                "company": company,
                "industry": industry,
                "analysis": final_analysis,
                "score": score,
                "recommendation": recommendation
            }
        }
    # ------------ 保存数据库 ------------
    try:
        async with AsyncSessionLocal() as tmp_db:
            # 会话不存在则创建
            session = await get_session_by_id(tmp_db, session_id)
            if not session:
                await save_session(tmp_db, session_id, create_session_title())

            # 保存消息
            await save_message(tmp_db, session_id, "user", question)
            if final_analysis:
                await save_message(tmp_db, session_id, "assistant", json.dumps(result_data,ensure_ascii=False))
    except Exception as e:
        logger.error(f"保存消息到数据库失败: {e}")
        # 不中断，继续返回结果
    logger.info(f"处理完成，结果类型: {result_data.get('type')}")
    return result_data

def create_session_title()->str:
    return f"会话：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"