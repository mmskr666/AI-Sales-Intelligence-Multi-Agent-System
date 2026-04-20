import asyncio
from tools.logger import logger
async def run_mcp_agent(llm_with_tools, tools_map, user_input):
    logger.info("Start running MCP agent")
    if not isinstance(user_input, str):
        user_input = str(user_input)

    messages = [
        {"role": "user", "content": user_input}
    ]
    logger.info("准备开始请求")
    try:
        # 发起初次请求
        response = await llm_with_tools.ainvoke(messages)

        # 无工具调用
        if not response.tool_calls:
            return response.content

        tool_messages = []

        for call in response.tool_calls:
            tool_name = call["name"]
            args = call["args"]
            tool_call_id = call["id"]

            # 调用工具函数
            tool = tools_map[tool_name]
            tool_result = await tool.ainvoke(args)

            # 确保工具返回的是最终结果，不是协程
            if asyncio.iscoroutine(tool_result):
                tool_result = await tool_result

            tool_messages.append({
                "role": "tool",
                "name": tool_name,
                "content": str(tool_result),
                "tool_call_id": tool_call_id
            })

        messages.append(response)
        messages.extend(tool_messages)

        # 发起最终响应
        final_response = await llm_with_tools.ainvoke(messages)

        # 确保最终响应的内容正确

        if asyncio.iscoroutine(final_response.content):
            final_response.content = await final_response.content

        return final_response.content

    except Exception as e:
        logger.error(f"运行MCP代理失败: {e}")
        return {"error": f"运行MCP代理失败: {e}"}