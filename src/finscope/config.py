from typing import Literal

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAgentSettings(BaseSettings):
    api_key: SecretStr | None = None
    model: str
    provider: Literal["ollama", "groq", "openai"] = "ollama"
    temperature: float = Field(default=0.1, ge=0, le=2)
    timeout_seconds: int = Field(default=60, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class WebResearchAgentSettings(BaseAgentSettings):
    model_config = SettingsConfigDict(
        env_prefix="WEB_RESEARCH_",
    )


class WebScrapingSettings(BaseSettings):
    base_url: str = Field(default="http://localhost:11235")
    api_token: SecretStr
    timeout_seconds: int
