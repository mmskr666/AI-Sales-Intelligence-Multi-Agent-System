from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from model.node_model import Industry
from prompt.industry_prompt import industry_prompt
from rag.rag_store import bm25, corpus, all_knowledge
from rag.rag_tools import rewrite, multi_query, hybrid_search, rerank_cross_encoder
from rag.retriever import get_retriever
from state.SalesState import SalesState
from tools.llm_factory import create_llm_with_tools, create_llm
from tools.logger import logger
from tools.mcp_tools import industry_tool
from tools.memory_store import get_node_memory, save_node_memory, get_rag_memory, save_rag_memory, get_long_memory
from tools.retriever_store import retriever
from tools.retry import retry
from tools.timeout import run_with_timeout, task
from tools.executor import execute_with_graph

parser = PydanticOutputParser(pydantic_object=Industry)
prompt_industry = ChatPromptTemplate.from_messages(
    [
        ("system",f"{industry_prompt},用户长期特征：{{long_memory}}"),
        ("human","用户输入：{input}\n{format_constructions}")
    ]
).partial(format_constructions=parser.get_format_instructions())

chain = prompt_industry | create_llm() | parser
llm_with_tools,tools_map = create_llm_with_tools([industry_tool])
def industry_node(state:SalesState):
    logger.debug("👉 Industry Agent")
    cache = get_node_memory(state["session_id"], "industry", state["input"])
    long_memory = get_long_memory(state["session_id"])
    text = state["input"]
    knowledge = []
    rank_docs = []
    if not cache:
        response:Industry = chain.invoke({"input":state["input"],"long_memory":long_memory})
        try:
            rag_cache = get_rag_memory(state["session_id"], text)
            if rag_cache:
                rank_docs = rag_cache
            else:
                rewrite_text = rewrite(text)
                logger.debug(f"rewrite后的问题：{rewrite_text}")
                questions = multi_query(rewrite_text)
                logger.debug(f"multi后的问题：{questions}")

                for question in questions:
                    docs = hybrid_search(question, retriever,bm25=bm25,corpus=corpus,docs=all_knowledge,k=3)
                    knowledge.extend(docs)
                rank_docs = rank_docs + rerank_cross_encoder(rewrite_text,knowledge)
            content = execute_with_graph(task(llm_with_tools, tools_map, response.name), state, "industry")
            save_rag_memory(state["session_id"],text,rank_docs)
            prompt = f"你是一个行业分析大师，请基于以下资料进行分析：行业基本信息：{content}\n行业信息知识库：{rank_docs}.请给出一百字内的简洁分析"
            industry_info = create_llm().invoke(prompt)
            logger.debug(f"最终行业信息：{industry_info.content}")
        except Exception as e:
            return {
                "industry_info": "未获取到行业信息，降低对应评分",
                "fail_node": state.get("fail_node",[])+["industry"]
            }
        save_node_memory(state["session_id"], "industry",text,industry_info.content)
        return {
            "industry_info":industry_info.content
        }
    return {
        "industry_info":cache
    }

