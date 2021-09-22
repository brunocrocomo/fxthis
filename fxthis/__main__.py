import logging
import re

from telegram.ext import Updater, CommandHandler
from telegram.ext.filters import MessageEntity

from .webdriver import load_tweet_description
from .error import FxThisError
from . import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

twitter_url_regex = re.compile(r"http(?:s)?:\/\/(?:www.)?twitter\.com\/?")


def parse_urls(message):
    url_entities = {}

    if message.entities is not None:
        url_entities.update(message.parse_entities([MessageEntity.URL]))

    if message.caption_entities is not None:
        url_entities.update(message.parse_entities([MessageEntity.URL]))

    return list(url_entities.values())


def fx(update, context):
    try:
        if update.message is None:
            raise FxThisError("Não foi possível processar o comando /fx.")

        if update.message.reply_to_message is not None:
            urls = parse_urls(update.message.reply_to_message)
        else:
            urls = parse_urls(update.message)

        if len(urls) <= 0:
            raise FxThisError("Só trabalho com links.")

        tweet_url = urls[0]
        match = twitter_url_regex.search(tweet_url)

        if match is None:
            raise FxThisError("Isso não parece ser um link do Twitter.")

        tweet_description = load_tweet_description(tweet_url)
        fixed_tweet_url = tweet_url.replace("twitter", "fxtwitter")

        update.message.reply_text(
            f"{fixed_tweet_url}\n\n{tweet_description}", quote=False
        )

    except FxThisError as err:
        update.message.reply_text(str(err), quote=True)


def error_handler(update, context):
    logging.error(str(context.error))


def main():
    updater = Updater(config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("fx", fx))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
