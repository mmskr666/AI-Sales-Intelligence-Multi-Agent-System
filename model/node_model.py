from pydantic import BaseModel, Field


class Plan(BaseModel):
    tasks:list[str] = Field(description="任务需要调用的模块")

class Company(BaseModel):
    name:str = Field(description="公司名称")

class News(BaseModel):
    keyword:str = Field(description="新闻关键字")

class Industry(BaseModel):
    name:str = Field(description="行业名称")
