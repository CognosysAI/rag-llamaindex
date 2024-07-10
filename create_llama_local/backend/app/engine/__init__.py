import os
from llama_index.core.settings import Settings
from llama_index.core.agent import AgentRunner
from llama_index.core.tools.query_engine import QueryEngineTool
from app.engine.tools import ToolFactory
from app.engine.index import get_index
from typing import Optional


def get_chat_engine(user_id: str, top_k: Optional[int] = None):
    system_prompt = os.getenv("SYSTEM_PROMPT")
    top_k_value = top_k if top_k is not None else int(os.getenv("TOP_K", "3"))
    tools = []

    # Add query tool if index exists
    index = get_index(user_id)
    if index is not None:
        query_engine = index.as_query_engine(similarity_top_k=int(top_k_value))
        query_engine_tool = QueryEngineTool.from_defaults(query_engine=query_engine)
        tools.append(query_engine_tool)

    # Add additional tools
    tools += ToolFactory.from_env()

    return AgentRunner.from_llm(
        llm=Settings.llm,
        tools=tools,
        system_prompt=system_prompt,
        verbose=True,
    )
