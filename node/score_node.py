from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Score
from prompt.score_prompt import score_prompt
from state.SalesState import SalesState
from tools.llm_factory import create_llm
from tools.logger import logger
from tools.memory_store import get_user_memory, get_long_memory

parser = PydanticOutputParser(pydantic_object=Score)

prompt = ChatPromptTemplate.from_messages([
    ("system",f"{score_prompt},用户长期特征：{{long_memory}}"),
    ("human","用户输入：{text}\n历史对话：{history}\n公司信息：{company}\n行业信息：{industry}\n相关新闻：{news}\n{format_constructions}")
]).partial(format_constructions=parser.get_format_instructions())

chain = prompt | create_llm() | parser

def score_node(state:SalesState):
    logger.debug("👉 score_node")
    history = get_user_memory(state["session_id"])
    long_memory =get_long_memory(state["session_id"])
    response:Score = chain.invoke({"text":state["input"],
                                   "company":state.get("company_info","如果信息缺失，请降低评分"),
                                   "industry":state.get("industry_info","如果信息缺失，请降低评分"),
                                   "news":state.get("news_info","如果信息缺失，请降低评分"),
                                   "history":history,
                                   "long_memory":long_memory
                                   })
    return {
        "score":response.score,
        "level":response.level,
        "reason":response.reason
    }