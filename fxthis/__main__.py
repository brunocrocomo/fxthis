import re

from telegram.ext import Updater, CommandHandler
from telegram.ext.filters import MessageEntity

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from . import config


options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(config.CHROME_DRIVER_PATH, options=options)


twitter_url_regex = re.compile(r"http(?:s)?:\/\/(?:www.)?twitter\.com\/?")

TWEET_LOAD_TIMEOUT = 5


def parse_urls(message):
    url_entities = {}

    if message.entities is not None:
        url_entities.update(message.parse_entities([MessageEntity.URL]))

    if message.caption_entities is not None:
        url_entities.update(message.parse_entities([MessageEntity.URL]))

    return list(url_entities.values())


def fx(update, context):
    assert update.message is not None

    if update.message.reply_to_message is not None:
        urls = parse_urls(update.message.reply_to_message)
    else:
        urls = parse_urls(update.message)

    assert len(urls) > 0, "Sem link, sem trabalho."

    tweet_url = urls[0]

    match = twitter_url_regex.search(tweet_url)
    assert match is not None, "Isso não parece ser um link do Twitter."

    driver.get(tweet_url)
    try:
        element = WebDriverWait(driver, TWEET_LOAD_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//meta[@property='og:description']")
            )
        )
        description = element.get_attribute("content")
    except TimeoutException:
        description = "Não foi possível carregar o texto do Tweet."

    fixed_tweet_url = tweet_url.replace("twitter", "fxtwitter")
    update.message.reply_text(f"{fixed_tweet_url}\n\n{description}", quote=False)


def error_handler(update, context):
    assert update.message is not None
    update.message.reply_text(str(context.error), quote=True)


def main():

    updater = Updater(config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("fx", fx))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
