from pydantic import BaseModel, HttpUrl, AwareDatetime


class ScrapeRequest(BaseModel):
    url: HttpUrl


class ScrapeResult(BaseModel):
    url: HttpUrl
    title: str | None
    markdown: str
    scraped_at: AwareDatetime