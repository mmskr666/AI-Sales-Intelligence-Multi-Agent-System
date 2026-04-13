from typing import TypedDict, Any, Annotated
import operator

class SalesState(TypedDict):
    input:str
    session_id:str
    task:list[str]

    company_info:dict[str,Any]
    industry_info:dict[str,Any]
    news_info:dict[str,Any]

    analysis:dict[str,Any]
    score:int
    level:str
    reason:str

    merge_ready:bool
    fail_node: Annotated[list[str], operator.add]
    result:str