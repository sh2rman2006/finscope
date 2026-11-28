from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from finscope.config import AppBaseSettings


class WebScrapingSettings(AppBaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WEB_SCRAPING_",
    )

    base_url: str = "http://localhost:11235"
    api_token: SecretStr | None = None
    timeout_seconds: int = Field(default=60, gt=0)
