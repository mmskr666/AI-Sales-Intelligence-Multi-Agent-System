from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Industry
from node.base_mcp_agent import run_mcp_agent
from prompt.industry_prompt import industry_prompt
from state.SalesState import SalesState
from tools.cache import set_cache, get_cache
from tools.llm_factory import create_llm_with_tools, create_llm
from tools.logger import logger
from tools.mcp_tools import industry_tool
from tools.retry import retry
from tools.timeout import run_with_timeout, task

parser = PydanticOutputParser(pydantic_object=Industry)

prompt_industry = ChatPromptTemplate.from_messages(
    [
        ("system",industry_prompt),
        ("human","用户输入：{input}\n{format_constructions}")
    ]
).partial(format_constructions=parser.get_format_instructions())

chain = prompt_industry | create_llm() | parser
llm_with_tools,tools_map = create_llm_with_tools([industry_tool])
def industry_node(state:SalesState):
    logger.debug("👉 Industry Agent")
    cache_key = f'{state["session_id"]}:{state["input"]}'
    cache = get_cache(cache_key)
    if not cache:
        response:Industry = chain.invoke({"input":state["input"]})
        try:
            # task = run_mcp_agent(llm_with_tools, tools_map, response)
            # content = retry(lambda: run_with_timeout(task))
            # content = retry(lambda: run_mcp_agent(llm_with_tools, tools_map, response))
            from tools.executor import execute_with_graph
            content = execute_with_graph(task(llm_with_tools, tools_map, state["input"]), state, "news")
        except Exception as e:
            return {
                "industry_info": "未获取到行业信息，降低对应评分",
                "fail_node": state.get("fail_node",[])+["industry"]
            }
        set_cache(cache_key, content)
        return {
            "industry_info":content
        }
    return {
        "industry_info":cache
    }
