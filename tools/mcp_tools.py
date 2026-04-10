from langchain.tools import tool

from tools.api import get_company, get_news, get_industry


@tool(description="查询公司信息")
def company_tool(company_name:str):
    return get_company(company_name)

@tool(description="根据关键字查询相关新闻")
def news_tool(query:str):
    return get_news(query)

@tool(description="查询相关行业")
def industry_tool(industry_name:str):
    return get_industry(industry_name)