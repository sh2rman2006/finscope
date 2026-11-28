from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"


class AppBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        extra="ignore",
    )
