import time


def retry(func, max_retries=3, delay=1):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            time.sleep(delay)
    raise Exception(f"函数'{func.__name__}' 重试{max_retries}次后仍然失败")
