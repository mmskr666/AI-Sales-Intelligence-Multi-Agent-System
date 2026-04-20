from concurrent.futures.thread import ThreadPoolExecutor

from node.base_mcp_agent import run_mcp_agent


def run_with_timeout(func, timeout=10):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            result = future.result(timeout=timeout)
            return result
        except TimeoutError:
            raise TimeoutError("Function execution timed out.")

async def task(llm_with_tools, tools_map, text):
    return await run_mcp_agent(llm_with_tools, tools_map, text)