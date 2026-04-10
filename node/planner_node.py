from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Plan
from prompt.plan_prompt import planner_prompt
from state.SalesState import SalesState
from tools.llm_factory import create_llm
from tools.logger import logger

parser = PydanticOutputParser(pydantic_object=Plan)

prompt = ChatPromptTemplate.from_messages([
    ("system",planner_prompt),
    ("human","用户输入：{input}\n{format_constructions}"),
]).partial(format_constructions=parser.get_format_instructions())

planner_chain = prompt | create_llm() | parser

def planner_node(state:SalesState):
    logger.debug("👉 Planner Agent（LLM决策）")
    response:Plan = planner_chain.invoke({"input":state["input"]})
    return {
        "task": response.tasks
    }
