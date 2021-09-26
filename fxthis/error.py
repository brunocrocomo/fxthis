from dataclasses import dataclass


class FxThisError(Exception):
    pass


@dataclass
class TwitterAPIError(Exception):
    status_code: int
    response_json: str


class WebDriverError(Exception):
    pass
