import feedparser
import requests
from urllib.parse import urlencode
from config.configuration import NEWS_KEY
from tools.logger import logger
import http.client, urllib, json
from urllib.parse import urlencode, quote
def get_company(company_name:str):
    if company_name == "OpenAI":
        return {
            "name": "OpenAI",
            "industry": "AI",
            "funding": "数十亿美元",
            "desc": "人工智能研究公司"
        }
    if company_name == "Alibaba":
        return {
            "name": "Alibaba",
            "industry": "电商",
            "funding": "53.5亿美元",
            "desc": "中国最大的电商公司"
        }
    if company_name == "字节跳动":
        return {
            "name": "字节跳动",
            "industry": "社交",
            "funding": "53.5亿美元",
            "desc": "中国最大的社交公司"
        }
    return {
        "name": "示例公司",
        "industry": "示例行业",
        "funding": "0",
        "desc": "这是一个示例公司"
    }

def get_news(query:str):
    """
     NewsAPI.org 全球新闻API：支持中文关键词，免费额度高，无编码问题
     :param query: 搜索关键词
     :param num: 返回条数
     """
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "zh",  # 限定中文结果
        "pageSize": 3,
        "apiKey": NEWS_KEY,
        "sortBy": "publishedAt"  # 按时间排序，取最新
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        logger.debug(f"NewsAPI返回：{data}")

        if data.get("status") == "ok":
            articles = data["articles"]
            return {"news_info": ",".join([i["title"] for i in articles])}
        else:
            return {"news_info": f"查询失败：{data.get('message')}"}

    except Exception as e:
        logger.error(f"NewsAPI请求异常：{str(e)}")
        return {"news_info": f"请求异常：{str(e)}"}

def get_industry(industry_name:str):
    if industry_name == "人工智能" or industry_name == "AI" or industry_name == "ai行业":
        return {
            "name": "AI",
            "average_growth": "0.5"
        }
    return {
            "name": "示例行业",
            "average_growth": "0.5"
        }