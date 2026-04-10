from langchain.chat_models import init_chat_model

from config.configuration import API_KEY,BASE_URL,chat_model
from node.industry_node import industry_node
from tools.mcp_tools import company_tool, news_tool, industry_tool

llm = init_chat_model(
    chat_model,
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=0.7,
    timeout=60,
    max_tokens=1000
)
