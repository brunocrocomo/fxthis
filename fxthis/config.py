import json

with open("config.json", "r") as file:
    config = json.load(file)

TELEGRAM_BOT_TOKEN = config["telegramBotToken"]
TWITTER_API_TOKEN = config["twitterAPIToken"]
FIREFOX_BINARY_PATH = config["firefoxBinaryPath"]
GECKODRIVER_PATH = config["geckodriverPath"]
