from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage

from finscope.capabilities.web_scraping.exceptions import WebScrapingFailedError
from finscope.capabilities.web_search.exceptions import WebSearchError


@wrap_tool_call
async def handle_tool_errors(request, handler):
    try:
        return await handler(request)
    except (WebScrapingFailedError, WebSearchError) as e:
        return ToolMessage(
            content=str(e),
            tool_call_id=request.tool_call["id"],
            status="error",
        )
