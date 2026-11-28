import asyncio

from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_core.language_models import BaseChatModel

from finscope.agents.web_research.context import WebResearchContext
from finscope.agents.web_research.middleware import handle_tool_errors
from finscope.agents.web_research.prompts import research_prompt
from finscope.agents.web_research.settings import WebResearchAgentSettings
from finscope.agents.web_research.tools import build_web_research_tools
from finscope.capabilities.web_scraping.factory import create_web_scraping_service
from finscope.capabilities.web_scraping.service import WebScrapingService
from finscope.capabilities.web_search.factory import create_web_search_service
from finscope.capabilities.web_search.service import WebSearchService
from finscope.llm import create_chat_model


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
        context_schema=WebResearchContext,
        middleware=[
            research_prompt,
            handle_tool_errors,
            ToolCallLimitMiddleware(
                tool_name="web_search",
                run_limit=5,
                exit_behavior="continue",
            ),
            ToolCallLimitMiddleware(
                tool_name="web_scrape",
                run_limit=3,
                exit_behavior="continue",
            ),
        ],
    )


async def main():
    settings = WebResearchAgentSettings()
    model = create_chat_model(settings=settings)

    async with (
        create_web_search_service() as search_service,
        create_web_scraping_service() as scraping_service,
    ):
        agent = build_web_research_agent(
            model=model,
            web_search_service=search_service,
            web_scraping_service=scraping_service,
        )

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Исследуй последние финансовые "
                            "результаты NVIDIA."
                        ),
                    }
                ]
            },
            context=WebResearchContext(),
            config={"recursion_limit": 30},
        )

        for message in result["messages"]:
            message.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
