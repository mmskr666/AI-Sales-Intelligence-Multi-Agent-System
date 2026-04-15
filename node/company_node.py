from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Company
from prompt.company_prompt import company_prompt
from state.SalesState import SalesState
from tools.llm_factory import create_llm_with_tools, create_llm
from tools.logger import logger
from tools.mcp_tools import company_tool
from tools.memory_store import save_node_memory, get_node_memory, get_long_memory
from tools.timeout import run_with_timeout, task

parser = PydanticOutputParser(pydantic_object=Company)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",f"{company_prompt},用户长期特征：{{long_memory}}"),
        ("human","用户输入：{input}\n{format_constructions}")
    ]
).partial(format_constructions=parser.get_format_instructions())

company_chain = prompt | create_llm() | parser
llm_with_tools,tools_map = create_llm_with_tools([company_tool])

def company_node(state:SalesState):
    logger.debug("👉 Company Agent")
    text = state["input"]
    cache = get_node_memory(state["session_id"],"company",text)
    long_memory = get_long_memory(state["session_id"])
    if not cache:
        result:Company = company_chain.invoke({"input":text,"long_memory":long_memory})
        try:
            from tools.executor import execute_with_graph
            content = execute_with_graph(task(llm_with_tools, tools_map,result.name), state, "news")
        except Exception as e:
            return {
                "company_info": "未获取到公司信息，降低评分",
                "fail_node": state.get("fail_node",[])+["company"]
            }
        save_node_memory(state["session_id"],"company",state["input"],content)
        return {
            "company_info":content
        }
    return {
        "company_info":cache
    }
