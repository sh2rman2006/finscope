from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel

from finscope.agents.web_research.tools import build_web_research_tools
from finscope.capabilities.web_scraping.service import WebScrapingService
from finscope.capabilities.web_search.service import WebSearchService


def build_web_research_agent(
        model: BaseChatModel,
        web_search_service: WebSearchService,
        web_scraping_service: WebScrapingService,
):
    return create_agent(
        model=model,
        tools=build_web_research_tools(
            web_search_service,
            web_scraping_service,
        ),
    )
