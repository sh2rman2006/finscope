from pydantic import Field, HttpUrl
from pydantic_settings import SettingsConfigDict

from finscope.config import AppBaseSettings


class WebSearchSettings(AppBaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WEB_SEARCH_",
    )

    base_url: HttpUrl = HttpUrl("http://localhost:8080")
    timeout_seconds: int = Field(default=30, gt=0)
