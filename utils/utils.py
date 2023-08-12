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


"""
Available flags:
t: Short time (e.g 9:41 PM)
T: Long Time (e.g. 9:41:30 PM)
d: Short Date (e.g. 30/06/2021)
D: Long Date (e.g. 30 June 2021)
f (default): Short Date/Time (e.g. 30 June 2021 9:41 PM)
F: Long Date/Time (e.g. Wednesday, June, 30, 2021 9:41 PM)
R: Relative Time (e.g. 2 months ago, in an hour)
"""


def formatTimestamp(timestamp: int, flag: str):
    return f"<t:{timestamp}:{flag}>"
