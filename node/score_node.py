from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Score
from prompt.score_prompt import score_prompt
from state.SalesState import SalesState
from tools.llm_factory import create_llm
from tools.logger import logger

parser = PydanticOutputParser(pydantic_object=Score)

prompt = ChatPromptTemplate.from_messages([
    ("system",score_prompt),
    ("human","用户输入：{text}\n公司信息：{company}\n行业信息：{industry}\n相关新闻：{news}\n{format_constructions}")
]).partial(format_constructions=parser.get_format_instructions())

chain = prompt | create_llm() | parser

def score_node(state:SalesState):
    logger.debug("👉 score_node")
    response:Score = chain.invoke({"text":state["input"],
                                   "company":state.get("company_info","如果信息缺失，请降低评分"),
                                   "industry":state.get("industry_info","如果信息缺失，请降低评分"),
                                   "news":state.get("news_info","如果信息缺失，请降低评分")})
    return {
        "score":response.score,
        "level":response.level,
        "reason":response.reason
    }