from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .utils import parse_tweet_id
from .error import WebDriverError
from .dataclasses import Tweet, Data, Includes, User, Media
from . import config

TWEET_LOAD_TIMEOUT = 5

driver_options = Options()
driver_options.headless = True
driver = webdriver.Firefox(
    firefox_binary=config.FIREFOX_BINARY_PATH,
    executable_path=config.GECKODRIVER_PATH,
    options=driver_options,
)


def fetch_tweet_from_webpage(url):
    tweet_id = parse_tweet_id(url)

    if not url.startswith("http"):
        url = "https://" + url

    driver.get(url)

    try:
        element = WebDriverWait(driver, TWEET_LOAD_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//meta[@property='og:description']")
            )
        )
        tweet_text = element.get_attribute("content")
    except TimeoutException:
        raise WebDriverError("Não foi possível obter o texto do tweet")

    try:
        element = WebDriverWait(driver, TWEET_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//meta[@property='og:title']"))
        )
        tweet_user_name = element.get_attribute("content")
    except NoSuchElementException:
        raise WebDriverError("Não foi possível obter o nome do autor do tweet")

    try:
        element = WebDriverWait(driver, TWEET_LOAD_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//video"))
        )
        tweet_preview_image_url = element.get_attribute("poster")
    except NoSuchElementException:
        raise WebDriverError("Não foi possível obter a URL de preview do tweet")

    return Tweet(
        data=Data(id=tweet_id, text=tweet_text),
        includes=Includes(
            users=[User(name=tweet_user_name)],
            media=[Media(preview_image_url=tweet_preview_image_url)],
        ),
    )
