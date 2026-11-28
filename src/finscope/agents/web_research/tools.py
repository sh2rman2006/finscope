from langchain_core.tools import tool, BaseTool

from finscope.capabilities.web_scraping.schemas import ScrapeRequest, ScrapeResult
from finscope.capabilities.web_scraping.service import WebScrapingService
from finscope.capabilities.web_search.schemas import SearchRequest, SearchResult
from finscope.capabilities.web_search.service import WebSearchService


def build_web_search_tool(
        web_search_service: WebSearchService,
) -> BaseTool:
    @tool
    async def web_search(
            search_request: SearchRequest,
    ) -> list[SearchResult]:
        """Search the web for relevant information using keywords
        or natural language queries.

        Returns search results containing titles, URLs, snippets,
        and publication dates when available.

        Use this tool to discover relevant sources. To retrieve
        the full content of a page, use the web_scrape tool.
        """
        return await web_search_service.search(search_request)

    return web_search


def build_web_scraping_tool(web_scraping_service: WebScrapingService) -> BaseTool:
    @tool
    async def web_scrape(
            request: ScrapeRequest
    ) -> ScrapeResult:
        """Retrieve the content of a web page from a given URL.

        Use this tool when search result snippets provide insufficient
        information, or when detailed analysis and verification of
        a specific source are required.

        Use web_search first if you do not have a relevant URL.
        Only scrape pages relevant to the research objective.
        """
        return await web_scraping_service.scrape(request)

    return web_scrape


def build_web_research_tools(
        web_search_service: WebSearchService,
        web_scraping_service: WebScrapingService,
) -> list[BaseTool]:
    return [
        build_web_search_tool(web_search_service),
        build_web_scraping_tool(web_scraping_service),
    ]
