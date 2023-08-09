import os
import json

FILE_NAME = "config.json"


def setupGeneralConfig():
    if not os.path.exists(FILE_NAME):
        print(f"First time setup, creating {FILE_NAME}.")
        file = open(FILE_NAME, "w")
        file.write(json.dumps({"guild": "Main Guild ID here.", "owners": ("Replace with IDs for elevated privileges within the bot (without quotes).", "Another ID")}, sort_keys=True, indent=4))
        print(f"Please Update {FILE_NAME} with associated Settings listed in file.")


def getMainGuildID():
    with open(FILE_NAME) as file:
        data = json.load(file)
    return int(data["guild"])


def getOwnerIDs():
    with open(FILE_NAME) as file:
        data = json.load(file)
    return data["owners"]
