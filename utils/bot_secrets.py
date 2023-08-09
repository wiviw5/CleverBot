import os
import json

FILE_NAME = "secrets.json"


def setupSecretConfig():
    if not os.path.exists(FILE_NAME):
        print(f"First time setup, creating {FILE_NAME}.")
        file = open(FILE_NAME, "w")
        file.write(json.dumps({"bot_token": "Replace with your bot token."}, sort_keys=True, indent=4))
        print(f"Please Update {FILE_NAME} with associated Settings listed in file.")


def getBotToken():
    with open(FILE_NAME) as file:
        data = json.load(file)
    return data["bot_token"]
