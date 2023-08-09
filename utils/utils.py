from datetime import datetime

import discord

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


# This is done for how /commands support deferred responses, while buttons interactions do not.
async def sendReply(interaction: discord.Interaction, deferred: bool, ephemeral: bool, message: str):
    if deferred:
        await interaction.followup.send(message, ephemeral=ephemeral)
        return
    else:
        await interaction.response.send_message(message, ephemeral=ephemeral)
        return
