from langchain.chat_models import init_chat_model

from config.configuration import chat_model, API_KEY, BASE_URL


def create_llm_with_tools(tools):
    llm = init_chat_model(
    chat_model,
    api_key=API_KEY,
    base_url=BASE_URL,
    temperature=0.7,
    timeout=60,
    max_tokens=1000
    )
    tools_map = {tool.name: tool for tool in tools}
    return llm.bind_tools(tools),tools_map

def create_llm():
    llm = init_chat_model(
        chat_model,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=0.7,
        timeout=60,
        max_tokens=1000
    )
    return llm