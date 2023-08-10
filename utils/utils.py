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


# This function and two lines after returns out either a discord user, or None if it errors out, it uses deferred responses as well.
async def fetchUserFromID(interaction: discord.Interaction, userinput: str) -> discord.User | None:
    try:
        discord_id = int(userinput)
    except ValueError:
        await interaction.followup.send(f"Invalid input for user ID.", ephemeral=True)
        return None
    try:
        discord_user = await interaction.client.fetch_user(discord_id)
    except discord.NotFound:
        await interaction.followup.send(f"User was not found for {userinput}.", ephemeral=True)
        return None
    return discord_user


def getChannelFromID(interaction: discord.Interaction, channel_id: int) -> discord.TextChannel:
    return interaction.client.get_channel(channel_id)
