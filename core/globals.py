# core/globals.py
from prompt.company_prompt import company_prompt
from prompt.long_memory_prompt import long_memory_prompt
from prompt.multi_prompt import multi_prompt
from prompt.plan_prompt import planner_prompt
from prompt.rewrite_prompt import rewrite_prompt
from prompt.router_prompt import router_prompt
from tools.llm_factory import create_llm, create_llm_with_tools
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Industry, Score, Summary, Plan, Company, Memory
from prompt.industry_prompt import industry_prompt
from prompt.score_prompt import score_prompt
from prompt.summary_prompt import summary_prompt
from tools.mcp_tools import news_tool, company_tool, industry_tool

# ====================== 全局只初始化 1 次 ======================
# LLM
LLM = create_llm()
LLM_WITH_TOOLS, TOOLS_MAP = create_llm_with_tools([company_tool,news_tool,industry_tool])

# Industry
INDUSTRY_PARSER = PydanticOutputParser(pydantic_object=Industry)
INDUSTRY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", f"{industry_prompt},用户长期特征：{{long_memory}}"),
    ("human", "用户输入：{input}\\n{format_constructions}")
]).partial(format_constructions=INDUSTRY_PARSER.get_format_instructions())
INDUSTRY_CHAIN = INDUSTRY_PROMPT | LLM | INDUSTRY_PARSER

# Score
SCORE_PARSER = PydanticOutputParser(pydantic_object=Score)
SCORE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", f"{score_prompt},用户长期特征：{{long_memory}}"),
    ("human", "用户输入：{text}\\n历史对话：{history}\\n公司信息：{company}\\n行业信息：{industry}\\n相关新闻：{news}\\n{format_constructions}")
]).partial(format_constructions=SCORE_PARSER.get_format_instructions())
SCORE_CHAIN = SCORE_PROMPT | LLM | SCORE_PARSER

# Summary
SUMMARY_PARSER = PydanticOutputParser(pydantic_object=Summary)
SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", f"{summary_prompt},用户长期特征：{{long_memory}}"),
    ("human","""
        用户输入：{input}\n
        用户意图：{intent}\n
        历史对话：{history}\n
        公司信息：{company_info}\n
        行业信息：{industry_info}\n
        相关新闻：{news_info}\n
        参考评分:{score}\n
        评分等级:{level}\n
        原因:{reason}\n
        {format_constructions}
        """)
]).partial(format_constructions=SUMMARY_PARSER.get_format_instructions())
SUMMARY_CHAIN = SUMMARY_PROMPT | LLM | SUMMARY_PARSER

#Rewrite
prompt_rewrite = ChatPromptTemplate.from_messages([
    ("system",rewrite_prompt),
    ("human","用户输入：{text}")
])
REWRITE_CHAIN = prompt_rewrite | LLM

#multiQuery
prompt_multi = ChatPromptTemplate.from_messages([
    ("system",multi_prompt),
    ("human","用户输入：{text}")
])
MULTI_CHAIN = prompt_multi | LLM

#router
prompt = ChatPromptTemplate.from_messages([
    ("system",f"{router_prompt}\n用户长期特征：{{long_memory}}\n"),
    ("human","用户输入：{text}")
])
ROUTER_CHAIN = prompt | LLM

#PLANNER
PLANNER_PARSER = PydanticOutputParser(pydantic_object=Plan)
prompt = ChatPromptTemplate.from_messages([
    ("system",f"{planner_prompt}，用户长期特征：{{long_memory}}"),
    ("human","用户输入：{input}\n历史对话：{history}\n{format_constructions}"),
]).partial(format_constructions=PLANNER_PARSER.get_format_instructions())

PLANNER_CHAIN = prompt | LLM | PLANNER_PARSER

#COMPANY
COMPANY_PARSER = PydanticOutputParser(pydantic_object=Company)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",f"{company_prompt},用户长期特征：{{long_memory}}"),
        ("human","用户输入：{input}\n{format_constructions}")
    ]
).partial(format_constructions=COMPANY_PARSER.get_format_instructions())
COMPANY_CHAIN = prompt | LLM | COMPANY_PARSER


UPDATE_PARSER = PydanticOutputParser(pydantic_object=Memory)
prompt = ChatPromptTemplate.from_messages([
    ("system", long_memory_prompt),
    ("human", "历史对话：{history}\n{format_constructions}"),
]).partial(format_constructions=UPDATE_PARSER.get_format_instructions())
UPDATE_CHAIN = prompt | LLM | UPDATE_PARSER