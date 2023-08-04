from datetime import datetime

from utils.bot_config import setupGeneralConfig, getOwnerIDs
from utils.bot_secrets import setupSecretConfig


def getTime():
    now = datetime.now()
    currentTime = now.strftime("%m/%d/%y | %H:%M:%S")
    return currentTime


def loadConfigs():
    setupGeneralConfig()
    setupSecretConfig()


def isOwner(userid):
    for ownerID in getOwnerIDs():
        if int(ownerID) == int(userid):
            return True
    return False
