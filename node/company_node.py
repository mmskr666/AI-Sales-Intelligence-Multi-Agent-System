from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Company
from node.base_mcp_agent import run_mcp_agent
from prompt.company_prompt import company_prompt
from state.SalesState import SalesState
from tools.cache import get_cache, set_cache
from tools.llm_factory import create_llm_with_tools, create_llm
from tools.logger import logger
from tools.mcp_tools import company_tool
from tools.retry import retry
from tools.timeout import run_with_timeout

parser = PydanticOutputParser(pydantic_object=Company)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",company_prompt),
        ("human","用户输入：{input}\n{format_constructions}")
    ]
).partial(format_constructions=parser.get_format_instructions())

company_chain = prompt | create_llm() | parser
llm_with_tools,tools_map = create_llm_with_tools([company_tool])
def company_node(state:SalesState):
    logger.debug("👉 Company Agent")
    text = state["input"]
    cache_key = f'{state["session_id"]}:{text}'
    cache = get_cache(cache_key)
    if not cache:
        result:Company = company_chain.invoke({"input":text})
        try:
            # task = run_mcp_agent(llm_with_tools, tools_map, result.name)
            # content = retry(lambda: run_with_timeout(task))
            content = retry(lambda:run_mcp_agent(llm_with_tools,tools_map,result.name))
        except Exception as e:
            return {
                "company_info": "未获取到公司信息，降低评分",
                "fail_node": state.get("fail_node",[])+["company"]
            }
        set_cache(cache_key,content)
        return {
            "company_info":content
        }
    return {
        "company_info":cache
    }
