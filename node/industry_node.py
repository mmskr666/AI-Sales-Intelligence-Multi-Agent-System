from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Industry
from node.base_mcp_agent import run_mcp_agent
from prompt.industry_prompt import industry_prompt
from state.SalesState import SalesState
from tools.llm_factory import create_llm_with_tools, create_llm
from tools.logger import logger
from tools.mcp_tools import industry_tool

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
    response:Industry = chain.invoke({"input":state["input"]})
    content = run_mcp_agent(llm_with_tools,tools_map,response)
    return {
        "industry_info":content
    }