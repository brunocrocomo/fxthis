import re
from urllib.parse import urlparse

from .error import FxThisError

twitter_path_regex = re.compile(r"\/(?:#!\/)?(\w+)\/status(es)?\/(\d+)")


def parse_tweet_id(url):
    if not url.startswith("http"):
        url = "//" + url

    url_parse_result = urlparse(url)

    if url_parse_result.netloc != "twitter.com":
        raise FxThisError("Isso não parece ser um link do Twitter.")

    match = twitter_path_regex.match(url_parse_result.path)

    if match is None:
        raise FxThisError("Isso não parece ser um link de um Tweet.")

    return url_parse_result.path.split("/")[-1]
