from state.SalesState import SalesState
from tools.logger import logger


def summary_node(state:SalesState):
    logger.debug("👉 Summary Agent")
    finally_result =f"""
    === 销售价值分析报告 ===
    【公司信息】
    {state.get("company_info","未获取到公司信息")}
    【行业信息】
    {state.get("industry_info","未获取到行业信息")}
    【相关新闻】
    {state.get("news_info","未获取到新闻信息")}
    """
    return {
        "result": finally_result
    }
