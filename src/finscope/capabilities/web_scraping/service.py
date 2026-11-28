import datetime

import httpx
import structlog
from httpx import AsyncClient
from pydantic import ValidationError

from finscope.capabilities.web_scraping.exceptions import WebScrapingTimeoutError, WebScrapingFailedError, \
    WebScrapingInvalidResponseError
from finscope.capabilities.web_scraping.schemas import ScrapeRequest, ScrapeResult

logger = structlog.get_logger(__name__)


class WebScrapingService:
    def __init__(self, client: AsyncClient):
        self._client = client

    async def scrape(
            self,
            request: ScrapeRequest,
    ) -> ScrapeResult:
        try:
            response = await self._client.post(
                "/crawl",
                json={
                    "urls": [str(request.url)]
                },
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise WebScrapingTimeoutError(
                "Web scraping timed out"
            ) from exc

        except httpx.HTTPStatusError as e:
            logger.error(
                "web_scraping_http_error",
                status_code=e.response.status_code,
                response_body=e.response.text[:2000],
                target_url=str(request.url),
            )
            raise WebScrapingFailedError(
                f"Web scraping returned HTTP {e.response.status_code}"
            ) from e

        except httpx.RequestError as exc:
            raise WebScrapingFailedError(
                "Web scrap service is unavailable"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise WebScrapingInvalidResponseError(
                "Invalid JSON response"
            ) from exc

        return self._parse_result(data)

    @staticmethod
    def _parse_result(data: object) -> ScrapeResult:
        if not isinstance(data, dict):
            raise WebScrapingInvalidResponseError(
                "Expected JSON object"
            )

        results = data.get("results")

        if not isinstance(results, list) or len(results) != 1:
            raise WebScrapingInvalidResponseError(
                "Expected exactly one crawl result"
            )

        result = results[0]

        if not isinstance(result, dict):
            raise WebScrapingInvalidResponseError(
                "Invalid crawl result"
            )

        success = result.get("success")

        if not isinstance(success, bool):
            raise WebScrapingInvalidResponseError(
                "Missing or invalid success field"
            )

        if not success:
            raise WebScrapingFailedError(
                result.get("error_message") or "Page scraping failed"
            )

        markdown = result.get("markdown")

        if not isinstance(markdown, dict):
            raise WebScrapingInvalidResponseError(
                "Invalid markdown object"
            )

        content = markdown.get("raw_markdown")

        if not isinstance(content, str):
            raise WebScrapingInvalidResponseError(
                "Invalid raw_markdown field"
            )

        if not content.strip():
            raise WebScrapingFailedError(
                "Page contains no readable content"
            )

        metadata = result.get("metadata")

        if not isinstance(metadata, dict):
            metadata = {}

        try:
            return ScrapeResult.model_validate({
                "url": result.get("url"),
                "title": metadata.get("title"),
                "markdown": content,
                "scraped_at": datetime.datetime.now(datetime.timezone.utc),
            })
        except ValidationError as exc:
            raise WebScrapingInvalidResponseError(
                "Crawl result validation failed"
            ) from exc
