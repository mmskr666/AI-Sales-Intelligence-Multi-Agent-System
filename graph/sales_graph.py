from node.company_node import company_node
from node.industry_node import industry_node
from node.merge_node import merge_node
from node.news_node import news_node
from node.planner_node import planner_node
from node.router_node import router_node
from node.score_node import score_node
from node.summary_node import summary_node
from state.SalesState import SalesState
from langgraph.graph import StateGraph, END

def build_graph():
    graph = StateGraph(SalesState)
    graph.set_entry_point("router")

    graph.add_node("planner",planner_node)
    graph.add_node("company",company_node)
    graph.add_node("industry",industry_node)
    graph.add_node("news",news_node)
    graph.add_node("summary",summary_node)
    graph.add_node("score",score_node)
    graph.add_node("merge",merge_node)
    graph.add_node("router",router_node)
    def get_intent(state:SalesState):
        return state["intent"]
    graph.add_conditional_edges(
        "router",
        get_intent,
        {
            "build":"summary",
            "sales":"planner",
            "refuse":"summary"
        }
    )

    def get_tasks(state:SalesState):
        return state["task"]
    graph.add_conditional_edges(
        "planner",
        get_tasks, #真正要走的后续节点
        ["company","industry","news"] #参考内容
    )

    def get_company(state:SalesState):
        ready = state.get("merge_ready")
        if not ready:
            return "summary"
        else:
            return "score"
    graph.add_conditional_edges(
        "merge",
        get_company,
        {
            "summary":"summary",
            "score":"score"
        }
    )
    graph.add_edge("company","merge")
    graph.add_edge("industry","merge")
    graph.add_edge("news","merge")
    graph.add_edge("score","summary")
    graph.add_edge("summary",END)

    return graph.compile()