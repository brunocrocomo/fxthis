import logging

from telegram import InlineQueryResultVideo, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram.ext.filters import MessageEntity

from .api import tweet_lookup
from .webdriver import fetch_tweet_from_webpage
from .error import FxThisError, TwitterAPIError, WebDriverError
from . import config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


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

        tweet = None

        try:
            tweet = tweet_lookup(tweet_url)
        except TwitterAPIError as err:
            logging.error(f"Twitter API Error ({err.status_code}): {err.response_json}")

        if not tweet:
            try:
                logging.info("Fetching tweet information using webdriver.")
                tweet = fetch_tweet_from_webpage(tweet_url)
            except WebDriverError as err:
                logging.error(err)

        fixed_tweet_url = tweet_url.replace("twitter", "fxtwitter")

        if tweet:
            reply_text = f"{fixed_tweet_url}\n\n{tweet.data.text}"
        else:
            reply_text = fixed_tweet_url

        update.message.reply_text(reply_text, quote=False)

    except FxThisError as err:
        update.message.reply_text(str(err), quote=True)


def inline_query(update, context):
    if update.inline_query is None:
        return

    query = update.inline_query.query

    if query == "":
        return

    tweet = None

    try:
        tweet = tweet_lookup(query)
    except TwitterAPIError as err:
        logging.error(f"Twitter API Error ({err.status_code}): {err.response_json}")

    if not tweet:
        try:
            logging.info("Fetching tweet information using webdriver.")
            tweet = fetch_tweet_from_webpage(query)
        except WebDriverError as err:
            logging.error(err)

    if tweet is None:
        return

    fixed_tweet_url = query.replace("twitter", "fxtwitter")

    message_content = f"{fixed_tweet_url}\n{tweet.data.text}"

    update.inline_query.answer(
        [
            InlineQueryResultVideo(
                id="0",
                video_url=query,
                mime_type="text/html",
                thumb_url=tweet.includes.media[0].preview_image_url,
                title=tweet.includes.users[0].name,
                description=tweet.data.text,
                input_message_content=InputTextMessageContent(message_content),
            ),
        ]
    )


def error_handler(update, context):
    logging.error(str(context.error))


def main():
    updater = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("fx", fx))
    dispatcher.add_handler(InlineQueryHandler(inline_query))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
