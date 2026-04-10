from typing import TypedDict, Any


class SalesState(TypedDict):
    input:str
    session_id:str
    task:list[str]
    company_info:dict[str,Any]
    industry_info:dict[str,Any]
    news_info:dict[str,Any]
    analysis:dict[str,Any]
    result:str