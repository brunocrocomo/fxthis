import requests

from .utils import parse_tweet_id
from .error import TwitterAPIError
from .dataclasses import Tweet
from . import config


def tweet_lookup(url):
    tweet_id = parse_tweet_id(url)

    headers = {"Authorization": f"Bearer {config.TWITTER_API_TOKEN}"}

    params = {
        "expansions": "author_id,attachments.media_keys",
        "user.fields": "name",
        "media.fields": "preview_image_url",
    }

    response = requests.get(
        f"https://api.twitter.com/2/tweets/{tweet_id}", headers=headers, params=params
    )

    if response.status_code != 200:
        raise TwitterAPIError(
            status_code=response.status_code, response_json=response.json()
        )

    return Tweet(**response.json())
