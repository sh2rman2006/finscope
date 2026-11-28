from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx

from .service import WebSearchService
from .settings import WebSearchSettings


@asynccontextmanager
async def create_web_search_service(
        settings: WebSearchSettings | None = None,
) -> AsyncIterator[WebSearchService]:
    settings = settings or WebSearchSettings()

    async with httpx.AsyncClient(
            base_url=str(settings.base_url),
            timeout=settings.timeout_seconds,
            trust_env=False,
    ) as client:
        yield WebSearchService(client)
