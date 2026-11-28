import httpx
import structlog
from httpx import AsyncClient
from pydantic import ValidationError

from finscope.capabilities.web_search.exceptions import WebSearchTimeoutError, WebSearchUnavailableError, \
    WebSearchInvalidResponseError, WebSearchDegradedError
from finscope.capabilities.web_search.schemas import SearchRequest, SearchResult

logger = structlog.get_logger(__name__)


class WebSearchService:
    def __init__(self, client: AsyncClient):
        self._client = client

    async def search(
            self,
            request: SearchRequest,
    ) -> list[SearchResult]:
        try:
            response = await self._client.get(
                "/search",
                params={
                    "q": request.query,
                    "format": "json",
                },
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise WebSearchTimeoutError(
                "Web search timed out"
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise WebSearchUnavailableError(
                f"Web search returned HTTP {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise WebSearchUnavailableError(
                "Web search service is unavailable"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise WebSearchInvalidResponseError(
                "Invalid JSON response"
            ) from exc

        return self._parse_results(data, request.limit)

    @staticmethod
    def _parse_results(
            data: dict,
            limit: int,
    ) -> list[SearchResult]:
        if not isinstance(data, dict):
            raise WebSearchInvalidResponseError(
                "Expected JSON object"
            )

        unresponsive_engines = data.get("unresponsive_engines")

        if unresponsive_engines:
            logger.warning(
                "web_search_partial_failure",
                engines=unresponsive_engines,
            )

        results = data.get("results")

        if not isinstance(results, list):
            raise WebSearchInvalidResponseError(
                "Expected 'results' to be a list"
            )

        if not results and unresponsive_engines:
            raise WebSearchDegradedError(
                "No search results returned and some search engines "
                "are unavailable."
            )

        search_results: list[SearchResult] = []

        for result in results:
            try:
                if not isinstance(result, dict):
                    logger.warning("web_search_invalid_result")
                    continue

                search_result = SearchResult(
                    title=result.get("title"),
                    url=result.get("url"),
                    snippet=result.get("content") or "",
                    published_at=result.get("publishedDate"),
                    engines=result.get("engines") or [],
                )

                search_results.append(search_result)

            except ValidationError as exc:
                logger.warning(
                    "web_search_invalid_result",
                    error=str(exc),
                )
                continue

            if len(search_results) >= limit:
                break

        if results and not search_results:
            raise WebSearchInvalidResponseError("All search results are invalid")

        return search_results
