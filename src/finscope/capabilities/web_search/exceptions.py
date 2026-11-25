class WebSearchError(Exception):
    pass


class WebSearchTimeoutError(WebSearchError):
    pass


class WebSearchUnavailableError(WebSearchError):
    pass


class WebSearchInvalidResponseError(WebSearchError):
    pass
