import httpx
import pytest

from finscope.capabilities.web_search.schemas import SearchRequest
from finscope.capabilities.web_search.service import WebSearchService


@pytest.mark.asyncio
async def test_search_success():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/search"
        assert request.url.params["q"] == "Microsoft"
        assert request.url.params["format"] == "json"

        return httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "title": "Microsoft Annual Report",
                        "url": "https://microsoft.com/report",
                        "content": "Financial results",
                        "publishedDate": None,
                        "engines": ["google"],
                    }
                ],
                "unresponsive_engines": [],
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
            transport=transport,
            base_url="http://localhost:8080",
    ) as client:
        service = WebSearchService(client)
        results = await service.search(
            SearchRequest(query="Microsoft"),
        )

    assert len(results) == 1
    assert results[0].title == "Microsoft Annual Report"
    assert str(results[0].url) == "https://microsoft.com/report"
    assert results[0].snippet == "Financial results"
    assert results[0].published_at is None
    assert results[0].engines == ["google"]
