from sre_parse import State

from node.company_node import company_node
from node.industry_node import industry_node
from node.news_node import news_node
from node.planner_node import planner_node
from node.summary_node import summary_node
from state.SalesState import SalesState
from langgraph.graph import StateGraph, END

def build_graph():
    graph = StateGraph(SalesState)
    graph.set_entry_point("planner")

    graph.add_node("planner",planner_node)
    graph.add_node("company",company_node)
    graph.add_node("industry",industry_node)
    graph.add_node("news",news_node)
    graph.add_node("summary",summary_node)

    def get_tasks(state:SalesState):
        return state["task"]
    graph.add_conditional_edges(
        "planner",
        get_tasks,
        ["company","industry","news"]
    )
    graph.add_edge("company","summary")
    graph.add_edge("industry","summary")
    graph.add_edge("news","summary")
    graph.add_edge("summary",END)

    return graph.compile()