from pydantic import BaseModel, Field


class Plan(BaseModel):
    tasks:list[str]  = Field(description="任务需要调用的模块")

class Company(BaseModel):
    name:str = Field(description="公司名称")

class News(BaseModel):
    keyword:str = Field(description="新闻关键字")

class Industry(BaseModel):
    name:str = Field(description="行业名称")

class Summary(BaseModel):
    company: str = Field(description="公司名称")
    industry: str = Field(description="行业名称")
    analysis: str = Field(description="分析结果/闲聊内容/拒答内容")
    score: int = Field(description="评分")
    recommendation: str = Field(description="推荐结果")

class Score(BaseModel):
    score:int = Field(description="评分(0-100)")
    level:str = Field(description="等级(低价值客户/中价值客户/高价值客户)")
    reason:str = Field(description="评分评级原因")

class Memory(BaseModel):
    interests: list = Field(description="感兴趣的行业")
    companies: list = Field(description="感兴趣的公司")
    intent: str = Field(description="用户意图")
    style: str = Field(description="用户风格")
    user: str = Field(description="用户信息")