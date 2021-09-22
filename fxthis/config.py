import json

with open("config.json", "r") as file:
    config = json.load(file)

TOKEN = config["token"]
FIREFOX_BINARY_PATH = config["firefoxBinaryPath"]
GECKODRIVER_PATH = config["geckodriverPath"]
