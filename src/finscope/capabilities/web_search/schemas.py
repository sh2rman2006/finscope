from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class SearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    title: str
    url: HttpUrl
    snippet: str = ""
    published_at: datetime | None = None
    engines: list[str] = Field(default_factory=list)
