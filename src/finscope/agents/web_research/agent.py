from langchain_core.language_models import BaseChatModel
from langgraph.graph.state import CompiledStateGraph


def build_web_research_agent(
        chat: BaseChatModel,
) -> CompiledStateGraph:
    ...
