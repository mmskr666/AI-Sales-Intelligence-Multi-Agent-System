from langchain_core.prompts import ChatPromptTemplate

from prompt.router_prompt import router_prompt
from state.SalesState import SalesState
from tools.memory_store import llm, get_long_memory

prompt = ChatPromptTemplate.from_messages([
    ("system",f"{router_prompt}\n用户长期特征：{{long_memory}}\n"),
    ("human","用户输入：{text}")
])
chain = prompt | llm
def router_node(state:SalesState):
    long_memory = get_long_memory(state["session_id"])
    result = chain.invoke({"text":state["input"],"long_memory":long_memory}).content
    return {
        "intent":result
    }