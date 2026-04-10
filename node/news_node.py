from node.base_mcp_agent import run_mcp_agent
from state.SalesState import SalesState
from tools.llm_factory import create_llm_with_tools
from tools.logger import logger
from tools.mcp_tools import news_tool

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
    content = run_mcp_agent(llm_with_tools,tools_map,state["input"])
    return {
        "news_info" : content
    }
