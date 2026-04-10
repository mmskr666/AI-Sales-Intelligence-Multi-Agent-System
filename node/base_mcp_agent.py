def run_mcp_agent(llm_with_tools,tools_map,user_input):
    if not isinstance(user_input, str):
        user_input = str(user_input)

    messages = [
        {"role": "user", "content": user_input}
    ]

    response = llm_with_tools.invoke(messages)

    # 无工具调用
    if not response.tool_calls:
        return response.content

    tool_messages = []

    for call in response.tool_calls:
        tool_name = call["name"]
        args = call["args"]
        tool_call_id = call["id"]

        # ✅ 正确：调用工具函数
        tool = tools_map[tool_name]
        tool_result = tool.invoke(args)

        tool_messages.append({
            "role": "tool",
            "name": tool_name,
            "content": str(tool_result),
            "tool_call_id": tool_call_id
        })

    messages.append(response)
    messages.extend(tool_messages)

    final_response = llm_with_tools.invoke(messages)

    return final_response.content