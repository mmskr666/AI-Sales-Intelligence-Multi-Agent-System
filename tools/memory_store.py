import hashlib
import json

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from model.node_model import Memory
from prompt.long_memory_prompt import long_memory_prompt
from tools.llm_factory import create_llm
from tools.redis_store import redis_client

MAX_LENGTH = 15
def save_user_memory(session_id,role,content):
    s_id = f"session:{session_id}"
    message = {
        "role":role,
        "content":content
    }
    handle_message = json.dumps(message)
    redis_client.lpush(s_id,handle_message)
    redis_client.ltrim(s_id,0,MAX_LENGTH-1)
    redis_client.expire(s_id,3600)

def get_user_memory(session_id):
    s_id = f"session:{session_id}"
    messages = redis_client.lrange(s_id,0,MAX_LENGTH-1)
    messages.reverse()
    return [json.loads(item) for item in messages]

def clear_user_memory(session_id):
    s_id = f"session:{session_id}"
    redis_client.delete(s_id)

def save_rag_memory(session_id,text,docs:list):
    rag_id = f"rag:{session_id}"
    redis_client.hset(rag_id,text,json.dumps(docs))

def get_rag_memory(session_id,text):
    rag_id = f"rag:{session_id}"
    docs = redis_client.hget(rag_id,text)
    if docs:
        return json.loads(docs)
    return []
def clear_rag_memory(session_id):
    rag_id = f"rag:{session_id}"
    redis_client.delete(rag_id)

def make_key(module: str, session_id: str, text: str):
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return f"{module}:{session_id}:{text_hash}"

def save_node_memory(session_id,node_name,text,docs:list):
    node_id = make_key(node_name,session_id,text)

    redis_client.set(node_id,text)
    redis_client.expire(node_id,3600)

def get_node_memory(session_id,node_name,text):
    node_id = make_key(node_name,session_id,text)
    if redis_client.exists(node_id):
        redis_client.expire(node_id, 3600)
        return redis_client.get(node_id)
    return None

def get_long_memory(session_id):
    key = f"session:{session_id}:profile"
    data = redis_client.get(key)
    if not data:
        return {}
    return json.loads(data)
def save_long_memory(session_id,data):
    key = f"session:{session_id}:profile"
    redis_client.set(key,json.dumps(data),ex=7*24*3600)

llm = create_llm()
parser = PydanticOutputParser(pydantic_object=Memory)
prompt = ChatPromptTemplate.from_messages([
    ("system", long_memory_prompt),
    ("human", "历史对话：{history}\n{format_constructions}"),
]).partial(format_constructions=parser.get_format_instructions())
chain = prompt | llm | parser
def update_long_memory(session_id,history):
    key = f"session:{session_id}:profile"
    response:Memory = chain.invoke({"history":history})
    try:
        redis_client.set(key,json.dumps(response.model_dump(),ensure_ascii=False),ex=7*24*3600)
    except:
        pass

