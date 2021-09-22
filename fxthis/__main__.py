import logging

from telegram import InlineQueryResultVideo, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram.ext.filters import MessageEntity

from .webdriver import fetch_tweet_video_information
from .error import FxThisError
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
        tweet = fetch_tweet_video_information(tweet_url)

        if tweet is None:
            raise FxThisError("Isso não parece ser um link do Twitter.")

        fixed_tweet_url = tweet_url.replace("twitter", "fxtwitter")
        tweet_description = (
            tweet.description
            if not None
            else "Não foi possível carregar o texto do tweet."
        )

        update.message.reply_text(
            f"{fixed_tweet_url}\n\n{tweet_description}", quote=False
        )

    except FxThisError as err:
        update.message.reply_text(str(err), quote=True)


def inline_query(update, context):
    if update.inline_query is None:
        return

    query = update.inline_query.query

    if query == "":
        return

    tweet = fetch_tweet_video_information(query)

    if tweet is None:
        return

    if tweet.video_poster is None:
        return

    fixed_tweet_url = query.replace("twitter", "fxtwitter")
    tweet_description = (
        tweet.description if not None else "Não foi possível carregar o texto do tweet."
    )

    message_content = f"{fixed_tweet_url}\n\n{tweet_description}"

    update.inline_query.answer(
        [
            InlineQueryResultVideo(
                id="0",
                video_url=query,
                mime_type="text/html",
                thumb_url=tweet.video_poster,
                title=tweet.title,
                description=tweet.description,
                input_message_content=InputTextMessageContent(message_content),
            ),
        ]
    )


def error_handler(update, context):
    logging.error(str(context.error))


def main():
    updater = Updater(config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("fx", fx))
    dispatcher.add_handler(InlineQueryHandler(inline_query))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()


if __name__ == "__main__":
    main()
