import httpx
import pytest

from finscope.capabilities.web_search.exceptions import WebSearchInvalidResponseError, WebSearchUnavailableError, \
    WebSearchTimeoutError
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


@pytest.mark.asyncio
async def test_search_all_results_invalid(service_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "title": "Invalid URL",
                        "url": "invalid-url",
                    },
                    {
                        "title": "Missing URL",
                    },
                    {
                        "url": "https://example.com",
                    },
                    {
                        "title": None,
                        "url": None,
                    },
                    "invalid result type",
                ],
                "unresponsive_engines": [],
            },
        )

    service = service_factory(handler)
    with pytest.raises(WebSearchInvalidResponseError, match="All search results are invalid"):
        await service.search(
            SearchRequest(query="Microsoft", limit=2),
        )


@pytest.mark.parametrize("payload", [
    {},
    {"results": None},
    {"results": "invalid"},
    {"results": {}},
    [],
    None,
])
@pytest.mark.asyncio
async def test_search_skips_invalid_results(service_factory, payload):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json=payload,
        )

    service = service_factory(handler)
    with pytest.raises(WebSearchInvalidResponseError):
        await service.search(
            SearchRequest(query="Microsoft", limit=2),
        )


@pytest.mark.parametrize("status_code", [403, 429, 500, 503])
@pytest.mark.asyncio
async def test_search_skips_invalid_results(service_factory, status_code):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=status_code,
        )

    service = service_factory(handler)
    with pytest.raises(WebSearchUnavailableError):
        await service.search(
            SearchRequest(query="Microsoft", limit=2),
        )


@pytest.mark.asyncio
async def test_search_timeout(service_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout(
            "Request timed out",
            request=request,
        )

    service = service_factory(handler)

    with pytest.raises(WebSearchTimeoutError):
        await service.search(SearchRequest(query="Microsoft"))


@pytest.mark.asyncio
async def test_search_connection_error(service_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            "Connection refused",
            request=request,
        )

    service = service_factory(handler)

    with pytest.raises(WebSearchUnavailableError):
        await service.search(SearchRequest(query="Microsoft"))


@pytest.mark.asyncio
@pytest.mark.parametrize("content", [
    b"",
    b"invalid json",
    b"<html>Internal error</html>",
])
async def test_search_invalid_json(service_factory, content):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            content=content,
        )

    service = service_factory(handler)

    with pytest.raises(
            WebSearchInvalidResponseError,
            match="Invalid JSON response",
    ):
        await service.search(SearchRequest(query="Microsoft"))


@pytest.mark.asyncio
async def test_search_partial_engine_failure(service_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "results": [
                    {
                        "title": "Microsoft Annual Report",
                        "url": "https://microsoft.com/report",
                        "content": "Financial results",
                        "engines": ["google"],
                    },
                ],
                "unresponsive_engines": [
                    ["duckduckgo", "CAPTCHA"],
                    ["bing", "timeout"],
                ],
            },
        )

    service = service_factory(handler)

    results = await service.search(
        SearchRequest(query="Microsoft"),
    )

    assert len(results) == 1
    assert results[0].engines == ["google"]
