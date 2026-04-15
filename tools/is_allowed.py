import time

from tools.memory_store import redis_client

def is_allowed(key,limit:int =20,window:int =60):
    """
      key: IP or session_id
      limit: 最大请求数
      window: 时间窗口（秒）
      """

    now = time.time()
    redis_key = f"rate_limit:{key}"

    # 1. 添加当前请求时间
    redis_client.zadd(redis_key, {str(now): now})

    # 2. 删除窗口外的请求
    redis_client.zremrangebyscore(redis_key, 0, now - window)

    # 3. 获取当前窗口内请求数
    count = redis_client.zcard(redis_key)

    # 4. 设置过期（防止key堆积）
    redis_client.expire(redis_key, window)

    return count <= limit