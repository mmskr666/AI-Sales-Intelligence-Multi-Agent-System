
import requests
from config.configuration import  G_NEWS_KEY

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


def get_news(query: str):
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "zh",
        "country": "cn",
        "max": 3,
        "apikey": G_NEWS_KEY,
        "sortby": "publishedAt"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        articles = data.get("articles", [])

        # ✅ 修复：直接返回字符串，不要返回字典！
        titles = [a["title"] for a in articles]
        if not titles:
            return "未查询到相关新闻"
        return "，".join(titles)  # 字符串！

    except Exception as e:
        return f"查询新闻异常：{str(e)}"

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