import json
from starlette.responses import StreamingResponse
from fastapi import APIRouter
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

def generate_stream(session_id, question):
    response = graph.stream({
        "input": question,
        "session_id": session_id
    })
    for chunk in response:
            yield json.dumps(chunk, ensure_ascii=False) + "\n"