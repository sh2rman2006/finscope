from typing import Literal

from pydantic import SecretStr, Field

from finscope.config import AppBaseSettings


class BaseAgentSettings(AppBaseSettings):
    api_key: SecretStr | None = None
    model: str
    provider: Literal[
        "ollama", "groq", "openai", "google"
    ] = "ollama"
    temperature: float = Field(default=0.1, ge=0, le=2)
    timeout_seconds: int = Field(default=60, gt=0)
