from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from finscope.config import BaseAgentSettings


def create_chat_model(
        settings: BaseAgentSettings,
) -> BaseChatModel:
    if settings.model == "groq":
        return ChatGroq(
            model=settings.model,
            api_key=settings.api_key,
            temperature=settings.temperature,
            timeout=settings.timeout_seconds
        )

    if settings.model == "openai":
        return ChatOpenAI(
            model=settings.model,
            api_key=settings.api_key,
            temperature=settings.temperature,
            timeout=settings.timeout_seconds
        )

    return ChatOllama(
        model=settings.model,
        temperature=settings.temperature,
    )
