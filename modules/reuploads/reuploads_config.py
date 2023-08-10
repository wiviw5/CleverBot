"""
This file is a part of the module "Reuploads"

All Files related to this module:
cogs/reuploads.py
modules/reuploads/reuploads_utils.py
modules/reuploads/reuploads_config.py
modules/reuploads/reuploads_config.json

If you do not want the reuploads module, a future release will have a toggle within a config file. (otherwise just remove the files related to the module.)
"""
import os
import json

FILE_NAME = f"modules{os.sep}reuploads{os.sep}reuploads_config.json"


def setupReuploadsConfig():
    if not os.path.exists(FILE_NAME):
        print(f"First time setup, creating {FILE_NAME}.")
        file = open(FILE_NAME, "w")
        file.write(json.dumps({"default_sending_channel": "Remove the quotes, and replace with a ID of the default channel you'd like images sent into."}, sort_keys=True, indent=4))
        file.close()
        print(f"Please Update {FILE_NAME} with associated Settings listed in file. Or, if you do not want reuploads, follow the instructions in the files in the reuploads module.")
        quit()


def getDefaultReuploadChannel():
    with open(FILE_NAME) as file:
        data = json.load(file)
    return int(data["default_sending_channel"])
