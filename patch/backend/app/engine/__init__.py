import os
from llama_index.core.settings import Settings
from llama_index.core.agent import AgentRunner
from app.engine.tools import ToolFactory
from app.engine.index import get_index
from typing import Optional


def get_chat_engine(user_id: str, top_k: Optional[int] = None):
    system_prompt = os.getenv("SYSTEM_PROMPT")
    top_k_value = top_k if top_k is not None else int(os.getenv("TOP_K", "3"))

    index = get_index(user_id)
    if index is None:
        raise RuntimeError("Index is not found")

    tools = ToolFactory.from_env()

    # Use the context chat engine if no tools are provided
    if len(tools) == 0:
        from llama_index.core.chat_engine import CondensePlusContextChatEngine

        return CondensePlusContextChatEngine.from_defaults(
            retriever=index.as_retriever(top_k=top_k_value),
            system_prompt=system_prompt,
            llm=Settings.llm,
        )
    else:
        from llama_index.core.agent import AgentRunner
        from llama_index.core.tools.query_engine import QueryEngineTool

        # Add the query engine tool to the list of tools
        query_engine_tool = QueryEngineTool.from_defaults(
            query_engine=index.as_query_engine(similarity_top_k=top_k_value)
        )
        tools.append(query_engine_tool)
        return AgentRunner.from_llm(
            llm=Settings.llm,
            tools=tools,
            system_prompt=system_prompt,
            verbose=True,  # Show agent logs to console
        )
