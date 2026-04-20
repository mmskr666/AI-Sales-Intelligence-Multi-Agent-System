import asyncio
import time
from tools.logger import logger

# async def execute_with_graph(func,state,node_name,max_retries=3):
#     for i in range(max_retries):
#         try:
#             start_time = time.time()
#             result =  await func()
#             end_time = time.time()
#             logger.debug(f"{node_name}执行时间：{end_time - start_time}s")
#             return result
#         except Exception as e:
#             await asyncio.sleep(1)
#     return {
#         f"{node_name}_info":"未查询到相关内容，请降低评分",
#         "fail_node":state.get("fail_node",[])+[node_name]
#     }
# 修改 execute_with_graph 函数
import asyncio
import time
from typing import Any, Coroutine, Dict


async def execute_with_graph(func: Coroutine, state: Dict, node_name: str, max_retries: int = 3) -> Any:
    logger.info("进入execute_with_graph")
    for i in range(max_retries):
        try:
            start_time = time.time()

            # 确保 func 是协程，然后等待它
            if asyncio.iscoroutine(func):
                result = await func
            elif callable(func):
                # 如果是函数，调用它
                func_result = func()
                if asyncio.iscoroutine(func_result):
                    result = await func_result
                else:
                    result = func_result
            else:
                result = func

            # 再次检查结果是否是协程
            if asyncio.iscoroutine(result):
                result = await result

            end_time = time.time()
            print(f"{node_name}执行时间：{end_time - start_time}s")
            return result

        except Exception as e:
            print(f"{node_name} 第{i + 1}次重试失败: {e}")
            if i < max_retries - 1:
                await asyncio.sleep(1)

    # 所有重试都失败
    return {
        f"{node_name}_info": "未查询到相关内容，请降低评分",
        "fail_node": state.get("fail_node", []) + [node_name]
    }