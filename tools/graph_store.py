"""
图存储管理器 - 高性能最终版
服务启动时自动初始化Graph，用户请求0等待
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# ======================
# 全局单例管理器
# ======================
class GraphManager:
    _instance: Optional["GraphManager"] = None
    _instance_lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._graph = None
        return cls._instance

    async def initialize(self):
        """服务启动时预加载Graph"""
        if self._graph is None:
            logger.info("🚀 服务启动：预加载LangGraph...")
            start_time = datetime.now()

            try:
                from graph.sales_graph import build_graph
                self._graph = build_graph()

                elapsed = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ LangGraph初始化完成，耗时: {elapsed:.2f}秒")
            except Exception as e:
                logger.error(f"❌ LangGraph初始化失败: {e}", exc_info=True)
                raise

    async def get_graph(self):
        """获取已加载好的Graph（用户调用=秒回）"""
        if self._graph is None:
            await self.initialize()
        return self._graph


# ======================
# 全局单例
# ======================
_graph_manager = GraphManager()


# ======================
# 核心优化：启动自动加载
# ======================
async def startup_graph():
    await _graph_manager.initialize()


async def get_graph():
    return await _graph_manager.get_graph()


async def is_graph_initialized():
    return _graph_manager._graph is not None


# ======================
# 代理保持兼容
# ======================
class GraphProxy:
    def __getattr__(self, name):
        async def async_wrapper(*args, **kwargs):
            graph = await get_graph()
            method = getattr(graph, name)
            if asyncio.iscoroutinefunction(method):
                return await method(*args, **kwargs)
            else:
                return method(*args, **kwargs)
        return async_wrapper

    def __repr__(self):
        return f"<GraphProxy initialized={_graph_manager._graph is not None}>"


graph = GraphProxy()

__all__ = ["graph", "get_graph", "is_graph_initialized", "startup_graph"]