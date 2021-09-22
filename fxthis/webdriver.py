from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from . import config

TWEET_LOAD_TIMEOUT = 5

driver_options = Options()
driver_options.headless = True
driver = webdriver.Firefox(
    firefox_binary=config.FIREFOX_BINARY_PATH,
    executable_path=config.GECKODRIVER_PATH,
    options=driver_options,
)


def load_tweet_description(tweet_url):
    try:
        driver.get(tweet_url)
        element = WebDriverWait(driver, TWEET_LOAD_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//meta[@property='og:description']")
            )
        )
        description = element.get_attribute("content")
    except TimeoutException:
        description = "Não foi possível carregar o texto do Tweet."

    return description
