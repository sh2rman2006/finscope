from collections.abc import AsyncIterator, Callable
from contextlib import AsyncExitStack

import httpx
import pytest_asyncio

from finscope.capabilities.web_search.service import WebSearchService


@pytest_asyncio.fixture
async def service_factory() -> AsyncIterator[
    Callable[..., WebSearchService]
]:
    async with AsyncExitStack() as stack:
        def factory(
                handler: Callable[[httpx.Request], httpx.Response],
        ) -> WebSearchService:
            client = httpx.AsyncClient(
                transport=httpx.MockTransport(handler),
                base_url="http://localhost:8080",
            )

            stack.push_async_callback(client.aclose)

            return WebSearchService(client)

        yield factory
