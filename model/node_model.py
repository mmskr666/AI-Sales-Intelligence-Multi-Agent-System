from pydantic import BaseModel, Field


class Plan(BaseModel):
    tasks:list[str] = Field(description="任务需要调用的模块")

class Company(BaseModel):
    name:str = Field(description="公司名称")

class News(BaseModel):
    keyword:str = Field(description="新闻关键字")

class Industry(BaseModel):
    name:str = Field(description="行业名称")

class Summary(BaseModel):
    company: str = Field(description="公司名称")
    industry: str = Field(description="行业名称")
    analysis: str = Field(description="分析结果")
    score: int = Field(description="评分")
    recommendation: str = Field(description="推荐结果")
