from node.base_mcp_agent import run_mcp_agent
from state.SalesState import SalesState
from tools.llm_factory import create_llm_with_tools
from tools.logger import logger
from tools.mcp_tools import news_tool
from tools.memory_store import save_node_memory, get_node_memory
from tools.retry import retry
from tools.executor import execute_with_graph
from tools.timeout import run_with_timeout, task

llm_with_tools,tools_map = create_llm_with_tools([news_tool])

def news_node(state:SalesState):
    logger.debug("👉 News Agent")
    cache = get_node_memory(state["session_id"],"news",state["input"])
    if not cache:
        try:
            content = execute_with_graph(task(llm_with_tools, tools_map, state["input"]),state,"news")
            logger.debug(f"NewsAgent返回：{content}")
        except Exception as e:
            return {
                "news_info": "未获取到相关新闻，降低对应评分",
                "fail_node": state.get("fail_node",[])+["news"]
            }
        save_node_memory(state["session_id"],"news",state["input"],content)
        return {
            "news_info" : content
        }
    return {
        "news_info": cache
    }
