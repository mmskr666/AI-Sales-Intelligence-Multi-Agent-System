from langchain_core.prompts import ChatPromptTemplate

from core.globals import ROUTER_CHAIN
from prompt.router_prompt import router_prompt
from state.SalesState import SalesState
from tools.memory_store import get_long_memory
from tools.logger import logger
# prompt = ChatPromptTemplate.from_messages([
#     ("system",f"{router_prompt}\n用户长期特征：{{long_memory}}\n"),
#     ("human","用户输入：{text}")
# ])
# chain = prompt | llm
async def router_node(state:SalesState):
    logger.info("👉 Router Agent")
    long_memory = await get_long_memory(state["session_id"])
    result = await ROUTER_CHAIN.ainvoke({"text":state["input"],"long_memory":long_memory})
    content = result.content
    return {
        "intent":content
    }