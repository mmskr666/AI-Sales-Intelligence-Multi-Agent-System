from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tools.executor import execute_with_graph
from core.globals import COMPANY_CHAIN, LLM_WITH_TOOLS, TOOLS_MAP
from model.node_model import Company
from prompt.company_prompt import company_prompt
from state.SalesState import SalesState
from tools.llm_factory import create_llm_with_tools, create_llm
from tools.logger import logger
from tools.mcp_tools import company_tool
from tools.memory_store import save_node_memory, get_node_memory, get_long_memory
from tools.timeout import run_with_timeout, task

# parser = PydanticOutputParser(pydantic_object=Company)
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system",f"{company_prompt},用户长期特征：{{long_memory}}"),
#         ("human","用户输入：{input}\n{format_constructions}")
#     ]
# ).partial(format_constructions=parser.get_format_instructions())
# company_chain = prompt | create_llm() | parser
# llm_with_tools,tools_map = create_llm_with_tools([company_tool])

async def company_node(state:SalesState):
    logger.info("👉 Company Agent")
    text = state["input"]
    cache = await get_node_memory(state["session_id"],"company",text)
    long_memory = await get_long_memory(state["session_id"])
    if not cache:
        result:Company = await COMPANY_CHAIN.ainvoke({"input":text,"long_memory":long_memory})
        try:
            content = await execute_with_graph(task(LLM_WITH_TOOLS, TOOLS_MAP,result.name), state, "company")
        except Exception as e:
            return {
                "company_info": "未获取到公司信息，降低评分",
                "fail_node": state.get("fail_node",[])+["company"]
            }
        await save_node_memory(state["session_id"],"company",state["input"],content)
        return {
            "company_info":content
        }
    return {
        "company_info":cache
    }
