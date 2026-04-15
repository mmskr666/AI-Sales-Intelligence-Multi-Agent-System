from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Plan
from prompt.plan_prompt import planner_prompt
from state.SalesState import SalesState
from tools.llm_factory import create_llm
from tools.logger import logger
from tools.memory_store import get_user_memory, save_user_memory, get_long_memory

parser = PydanticOutputParser(pydantic_object=Plan)

prompt = ChatPromptTemplate.from_messages([
    ("system",f"{planner_prompt}，用户长期特征：{{long_memory}}"),
    ("human","用户输入：{input}\n历史对话：{history}\n{format_constructions}"),
]).partial(format_constructions=parser.get_format_instructions())

planner_chain = prompt | create_llm() | parser

def planner_node(state:SalesState):
    logger.debug("👉 Planner Agent（LLM决策）")
    long_memory = get_long_memory(state["session_id"])
    history = get_user_memory(state["session_id"])
    response:Plan = planner_chain.invoke({"input":state["input"],"history":history,"long_memory":long_memory})
    return {
        "task": response.tasks,
    }
