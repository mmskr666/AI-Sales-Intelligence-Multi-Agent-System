# tools/graph_store.py
"""
图存储管理器 - 简化版本
修复异步生成器问题
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
import threading

# 设置日志
logger = logging.getLogger(__name__)


# ======================
# 全局单例管理器
# ======================
class GraphManager:
    """
    图管理器 - 单例模式，确保图只初始化一次
    """
    _instance: Optional["GraphManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
                cls._instance._graph = None
                cls._instance._initialization_lock = asyncio.Lock()
        return cls._instance

    def __init__(self):
        # 在__new__中已经初始化
        pass

    async def get_graph(self):
        """
        获取图实例 - 惰性初始化
        只有第一次调用时才真正初始化图
        """
        if not self._initialized:
            async with self._initialization_lock:
                if not self._initialized:  # 双重检查锁
                    logger.info("开始初始化LangGraph...")
                    start_time = datetime.now()

                    try:
                        # 延迟导入，避免启动时加载
                        from graph.sales_graph import build_graph

                        # 构建图
                        self._graph = build_graph()
                        self._initialized = True

                        elapsed = (datetime.now() - start_time).total_seconds()
                        logger.info(f"LangGraph初始化完成，耗时: {elapsed:.2f}秒")

                    except Exception as e:
                        logger.error(f"初始化LangGraph失败: {e}", exc_info=True)
                        raise

        return self._graph

    async def is_initialized(self) -> bool:
        """检查图是否已初始化"""
        return self._initialized and self._graph is not None


# ======================
# 全局实例和导出函数
# ======================
_graph_manager = GraphManager()


async def get_graph():
    """
    获取图实例的主要函数
    """
    return await _graph_manager.get_graph()


async def is_graph_initialized() -> bool:
    """检查图是否已初始化"""
    return await _graph_manager.is_initialized()


# ======================
# 简化的代理对象
# ======================
class GraphProxy:
    """
    图代理类
    当访问属性时获取真正的图实例
    """

    def __getattr__(self, name):
        """动态获取图实例的属性"""

        # 返回一个异步函数，在调用时获取图实例
        async def async_wrapper(*args, **kwargs):
            graph = await _graph_manager.get_graph()
            method = getattr(graph, name)

            # 检查是否是异步方法
            if asyncio.iscoroutinefunction(method):
                return await method(*args, **kwargs)
            else:
                return method(*args, **kwargs)

        return async_wrapper

    def __repr__(self):
        return f"<GraphProxy initialized={_graph_manager._initialized}>"


# 创建代理实例
graph = GraphProxy()

# 导出
__all__ = [
    "graph",  # 保持与原来相同的导出名
    "get_graph",
    "is_graph_initialized"
]