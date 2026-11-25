import httpx
import pytest

from finscope.capabilities.web_search.schemas import SearchRequest


@pytest.mark.asyncio
async def test_search_success(service_factory):
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

    service = service_factory(handler)
    results = await service.search(
        SearchRequest(query="Microsoft"),
    )

    assert len(results) == 1
    assert results[0].title == "Microsoft Annual Report"
    assert str(results[0].url) == "https://microsoft.com/report"
    assert results[0].snippet == "Financial results"
    assert results[0].published_at is None
    assert results[0].engines == ["google"]


@pytest.mark.asyncio
async def test_search_respects_limit(service_factory):
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
                    } for _ in range(5)
                ],
                "unresponsive_engines": [],
            },
        )

    service = service_factory(handler)
    results = await service.search(
        SearchRequest(query="Microsoft", limit=2),
    )

    assert len(results) == 2
    assert results[0].title == "Microsoft Annual Report"
    assert str(results[0].url) == "https://microsoft.com/report"
    assert results[0].snippet == "Financial results"
    assert results[0].published_at is None
    assert results[0].engines == ["google"]


@pytest.mark.asyncio
async def test_search_empty_results(service_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "results": [],
                "unresponsive_engines": [],
            },
        )

    service = service_factory(handler)
    results = await service.search(
        SearchRequest(query="Microsoft"),
    )

    assert not results


@pytest.mark.asyncio
async def test_search_skips_invalid_results(service_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "title": "Invalid result",
                        "url": "invalid-url",
                    },
                    {
                        "title": "Microsoft Annual Report",
                        "url": "https://microsoft.com/report",
                        "content": "Financial results",
                    },
                    {
                        "title": "Invalid result without URL",
                    },
                    {
                        "title": "Microsoft Investor Relations",
                        "url": "https://microsoft.com/investor",
                    },
                ],
                "unresponsive_engines": [],
            },
        )

    service = service_factory(handler)
    results = await service.search(
        SearchRequest(query="Microsoft", limit=2),
    )

    assert len(results) == 2
