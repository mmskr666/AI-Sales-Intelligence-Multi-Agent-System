from state.SalesState import SalesState
from tools.logger import logger


def merge_node(state:SalesState):
    logger.debug("👉 Merge Node")
    company = state.get("company_info")
    industry = state.get("industry_info")
    news = state.get("news_info")

    # ✅ 必须三个数据【全部都有】才继续
    if not all([company, industry, news]):
        return {}  # 数据不全 → 不往下走

    # ✅ 数据齐全 → 标记可以进入评分/总结
    return {
        "merge_ready": True
    }
