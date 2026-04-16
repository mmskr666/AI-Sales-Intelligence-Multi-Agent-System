import datetime
import json
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
from tools.graph_store import graph
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
    return StreamingResponse(
        generate_stream(request.session_id, request.question),
        media_type="text/plain"
    )
@app_router.get("/get_sessions",summary="查询历史会话")
async def get_sessions_list(skip=0,limit:int=10,db = Depends(db_store.get_db)):
    sessions = await get_sessions(db,skip,limit)
    return success(sessions)

@app_router.get("/get_session/{session_id}")
async def get_session(session_id:str,db = Depends(db_store.get_db)):
    messages = await get_message(db,session_id)
    return success(messages)

async def generate_stream(session_id, question):
    # 用来存最终的 analysis 文本
    final_analysis = ""

    async for chunk in graph.astream({
        "input": question,
        "session_id": session_id
    }):
        final_analysis = ""
        logger.debug(f"----chunk:{chunk}")
        # 安全取出 result
        summary = chunk.get("summary",{})
        result = summary.get("result", {})
        # 取出 analysis（你要存的内容）
        analysis = result.get("analysis", "")

        # 拼接最终文本
        final_analysis += analysis

        # 流式返回给前端（可选）
        if analysis:
            yield json.dumps(chunk, ensure_ascii=False) + "\n"

    # ------------ 保存数据库 ------------
    try:


        async with AsyncSessionLocal() as tmp_db:
            # 会话不存在则创建
            session = await get_session_by_id(tmp_db, session_id)
            if not session:
                await save_session(tmp_db, session_id, create_session_title())

            # 🔥 直接存 analysis
            await save_message(tmp_db, session_id, "user", question)
            await save_message(tmp_db, session_id, "assistant", final_analysis)

    except Exception as e:
        print("保存失败：", e)
def create_session_title()->str:
    return f"会话：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"