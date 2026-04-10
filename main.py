from graph.sales_graph import build_graph

if __name__ == '__main__':
    graph = build_graph()
    result = graph.invoke({
        "input": "帮我查询ai行业新闻",
        "session_id": "123"
    })
    print("------------------------------")
    # print(result["task"])
    print(result["result"])