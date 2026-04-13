from node.base_mcp_agent import run_mcp_agent
from state.SalesState import SalesState
from tools.cache import set_cache, get_cache
from tools.llm_factory import create_llm_with_tools
from tools.logger import logger
from tools.mcp_tools import news_tool
from tools.retry import retry
from tools.executor import execute_with_graph
from tools.timeout import run_with_timeout, task

# parser = PydanticOutputParser(pydantic_object=News)
#
# prompt = ChatPromptTemplate.from_messages([
#     ("system",news_prompt),
#     ("human","用户输入：{input}\n{format_constructions}"),
# ]).partial(format_constructions=parser.get_format_instructions())
#
# chain = prompt | llm | parser

llm_with_tools,tools_map = create_llm_with_tools([news_tool])

def news_node(state:SalesState):
    logger.debug("👉 News Agent")
    cache_key = f'{state["session_id"]}:{state["input"]}'
    cache = get_cache(cache_key)
    if not cache:
        try:
            # content = retry(lambda:run_mcp_agent(llm_with_tools,tools_map,state["input"]))
            # content = retry(lambda:run_with_timeout(task(llm_with_tools, tools_map, state["input"])))
            content = execute_with_graph(task(llm_with_tools, tools_map, state["input"]),state,"news")
            logger.debug(f"NewsAgent返回：{content}")
        except Exception as e:
            return {
                "news_info": "未获取到相关新闻，降低对应评分",
                "fail_node": state.get("fail_node",[])+["news"]
            }
        set_cache(cache_key, content)
        return {
            "news_info" : content
        }
    return {
        "news_info": cache
    }
