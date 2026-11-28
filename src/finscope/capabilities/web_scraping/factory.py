from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx

from .service import WebScrapingService
from .settings import WebScrapingSettings


@asynccontextmanager
async def create_web_scraping_service(
        settings: WebScrapingSettings | None = None,
) -> AsyncIterator[WebScrapingService]:
    settings = settings or WebScrapingSettings()

    async with httpx.AsyncClient(
            base_url=str(settings.base_url),
            timeout=settings.timeout_seconds,
            trust_env=False,
            headers={
                "Authorization": (
                        f"Bearer {settings.api_token.get_secret_value()}"
                ),
            },
    ) as client:
        yield WebScrapingService(client)
