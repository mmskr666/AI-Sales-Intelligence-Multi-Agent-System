from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Summary
from prompt.summary_prompt import summary_prompt
from state.SalesState import SalesState
from tools.llm_factory import create_llm
from tools.logger import logger

parser = PydanticOutputParser(pydantic_object=Summary)

prompt_summary = ChatPromptTemplate.from_messages(
    [
        ("system",summary_prompt),
        ("human","用户输入：{input}\n公司信息：{company_info}\n行业信息：{industry_info}\n相关新闻：{news_info}\n{format_constructions}")
    ]
).partial(format_constructions=parser.get_format_instructions())

chain = prompt_summary | create_llm() | parser

def summary_node(state:SalesState):
    logger.debug("👉 Summary Agent")
    response:Summary = chain.invoke({"input":state["input"],"company_info":state["company_info"],"industry_info":state["industry_info"],"news_info":state["news_info"]})
    return {
        "result": response
    }
