import json

with open("config.json", "r") as file:
    config = json.load(file)

TOKEN = config["token"]
CHROME_DRIVER_PATH = config["chromeDriverPath"]
