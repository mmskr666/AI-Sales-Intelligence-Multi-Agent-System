from pydantic import BaseModel


class RequestData(BaseModel):
    """
    请求数据模型
    """
    question:str
    session_id:str