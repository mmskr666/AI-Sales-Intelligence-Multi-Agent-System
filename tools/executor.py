import time
from tools.logger import logger

def execute_with_graph(func,state,node_name,max_retries=3):
    for i in range(max_retries):
        try:
            start_time = time.time()
            result =  func()
            end_time = time.time()
            logger.debug(f"{node_name}执行时间：{end_time - start_time}s")
            return result
        except Exception as e:
            time.sleep(1)
    return {
        f"{node_name}_info":"未查询到相关内容，请降低评分",
        "fail_node":state.get("fail_node",[])+[node_name]
    }