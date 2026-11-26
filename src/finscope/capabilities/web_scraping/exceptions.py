class WebScrapingError(Exception):
    pass


class WebScrapingTimeoutError(WebScrapingError):
    pass


class WebScrapingUnavailableError(WebScrapingError):
    pass


class WebScrapingInvalidResponseError(WebScrapingError):
    pass


class WebScrapingFailedError(WebScrapingError):
    pass
