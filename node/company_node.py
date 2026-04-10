from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Company
from node.base_mcp_agent import run_mcp_agent
from prompt.company_prompt import company_prompt
from state.SalesState import SalesState
from tools.api import get_company
from tools.llm import llm
from tools.llm_factory import create_llm_with_tools
from tools.logger import logger
from tools.mcp_tools import company_tool

parser = PydanticOutputParser(pydantic_object=Company)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",company_prompt),
        ("human","用户输入：{input}\n{format_constructions}")
    ]
).partial(format_constructions=parser.get_format_instructions())

company_chain = prompt | llm | parser
llm_with_tools,tools_map = create_llm_with_tools([company_tool])
def company_node(state:SalesState):
    logger.debug("👉 Company Agent")
    text = state["input"]
    result:Company = company_chain.invoke({"input":text})
    content = run_mcp_agent(llm_with_tools,tools_map,result.name)
    return {
        "company_info":content
    }
