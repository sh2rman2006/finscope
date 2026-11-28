from datetime import date

from pydantic import BaseModel, Field, ConfigDict


class WebResearchContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    current_date: date = Field(default_factory=date.today)
