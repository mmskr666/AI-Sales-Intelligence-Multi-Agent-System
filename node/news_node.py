import asyncio

from core.globals import LLM_WITH_TOOLS, TOOLS_MAP
from state.SalesState import SalesState
from tools.logger import logger
from tools.memory_store import save_node_memory, get_node_memory
from tools.executor import execute_with_graph
from tools.timeout import task

# llm_with_tools,tools_map = create_llm_with_tools([news_tool])

async def news_node(state:SalesState):
    logger.info("👉 News Agent")
    cache = await get_node_memory(state["session_id"],"news",state["input"])
    if not cache:
        try:
            content = await execute_with_graph(task(LLM_WITH_TOOLS,TOOLS_MAP, state["input"]),state,"news")
            if asyncio.iscoroutine(content):
                content = await content
            logger.debug(f"NewsAgent返回：{content}")
        except Exception as e:
            return {
                "news_info": "未获取到相关新闻，降低对应评分",
                "fail_node": state.get("fail_node",[])+["news"]
            }
        await save_node_memory(state["session_id"],"news",state["input"],content)
        return {
            "news_info" : content
        }
    return {
        "news_info": cache
    }
