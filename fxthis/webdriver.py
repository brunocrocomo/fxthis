import re
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from . import config

TWEET_LOAD_TIMEOUT = 5

twitter_url_regex = re.compile(r"http(?:s)?:\/\/(?:www.)?twitter\.com\/?")

driver_options = Options()
driver_options.headless = True
driver = webdriver.Firefox(
    firefox_binary=config.FIREFOX_BINARY_PATH,
    executable_path=config.GECKODRIVER_PATH,
    options=driver_options,
)


@dataclass
class TweetVideoInformation:
    title: str
    description: str
    video_poster: str


def fetch_tweet_video_information(tweet_url):
    match = twitter_url_regex.search(tweet_url)

    if match is None:
        return None

    driver.get(tweet_url)

    try:
        element = WebDriverWait(driver, TWEET_LOAD_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//meta[@property='og:description']")
            )
        )
        tweet_description = element.get_attribute("content")
    except TimeoutException:
        tweet_description = None

    try:
        element = WebDriverWait(driver, TWEET_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//meta[@property='og:title']"))
        )
        tweet_title = element.get_attribute("content")
    except NoSuchElementException:
        tweet_title = None

    try:
        element = WebDriverWait(driver, TWEET_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//video"))
        )
        tweet_video_poster = element.get_attribute("poster")
    except NoSuchElementException:
        tweet_video_poster = None

    return TweetVideoInformation(tweet_title, tweet_description, tweet_video_poster)
