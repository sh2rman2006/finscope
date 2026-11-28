from pydantic_settings import SettingsConfigDict

from finscope.agents.settings import BaseAgentSettings


class WebResearchAgentSettings(BaseAgentSettings):
    model_config = SettingsConfigDict(
        env_prefix="WEB_RESEARCH_",
    )
