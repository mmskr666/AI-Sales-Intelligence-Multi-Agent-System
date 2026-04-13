from graph.sales_graph import build_graph

if __name__ == '__main__':
    graph = build_graph()
    result = graph.invoke({
        "input": "帮我查询一下字节跳动",
        "session_id": "123"
    })
    print("------------------------------")
    # print(result["task"])
    print(result["result"])