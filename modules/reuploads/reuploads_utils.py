"""
This file is a part of the module "Reuploads"

All Files related to this module:
cogs/reuploads.py
modules/reuploads/reuploads_utils.py
modules/reuploads/reuploads_config.py
modules/reuploads/reuploads_config.json

If you do not want the reuploads module, a future release will have a toggle within a config file. (otherwise just remove the files related to the module.)
"""
import io

import discord

from modules.reuploads.reuploads_config import getDefaultReuploadChannel
from utils.files_utils import getHashOfBytes, getFileSize, downloadURL, checkFileSize, getFileExtensionType
from utils.utils import getChannelFromID


async def sendFile(interaction: discord.Interaction, url, filename, channel, spoiler, source):
    returnedBytes = await downloadURL(url)
    if not checkFileSize(returnedBytes):
        await interaction.followup.send(f"### Failed Uploading file due to size limits by discord, details of upload are below.\n{source}\nOrigin URL: `{url}`\nHash: `{getHashOfBytes(returnedBytes.content)}` Size: `{getFileSize(returnedBytes.content)}", ephemeral=True)
        return
    finalFileName = getFileName(filename=filename, RB=returnedBytes, spoiler=spoiler)
    fileToSend = discord.File(io.BytesIO(returnedBytes.content), filename=finalFileName)
    if channel is None:
        channel = getDefaultChannel(interaction=interaction)
    await channel.send(f"{source}\nOrigin URL: `{url}`\nHash: `{getHashOfBytes(returnedBytes.content)}` Size: `{getFileSize(returnedBytes.content)}`", file=fileToSend)
    await interaction.followup.send(f"Successfully sent file!", ephemeral=True)


async def sendAvatar(interaction: discord.Interaction, userID, channel, spoiler, source):
    discUser = await interaction.client.fetch_user(int(userID))
    userAvatarURL = discUser.avatar.url
    modifiedSource = getFormattedUsernames(discUser)
    if source is not None:
        modifiedSource = f"{modifiedSource}\n`{source}`"
    await sendFile(interaction=interaction, url=userAvatarURL, filename=discUser.id, channel=channel, spoiler=spoiler, source=modifiedSource)


async def sendBanner(interaction: discord.Interaction, userID, channel, spoiler, source):
    discUser = await interaction.client.fetch_user(int(userID))
    userBannerURL = adjustPictureSizeDiscord(discUser.banner.url, 1024)
    modifiedSource = getFormattedUsernames(discUser)
    if source is not None:
        modifiedSource = f"{modifiedSource}\n`{source}`"
    await sendFile(interaction=interaction, url=userBannerURL, filename=discUser.id, channel=channel, spoiler=spoiler, source=modifiedSource)


def getFormattedUsernames(discord_user: discord.User) -> str:
    # Checking if it's not 0 (the sign they've still got a discriminator)
    if not discord_user.discriminator == "0":
        return f"`{discord_user.name}#{discord_user.discriminator}` | {discord_user.mention} | `{discord_user.id}`"
    # If the global name and the name are the same, global is "none" and shows up as None in the final mesage, this just removes that.
    if discord_user.global_name is None:
        return f"`{discord_user.name}` | {discord_user.mention} | `{discord_user.id}`"
    # Finally, returning a properly formatted string at the end here.
    return f"`{discord_user.name}` | `{discord_user.global_name}` | {discord_user.mention} | `{discord_user.id}`"


def adjustPictureSizeDiscord(url, requestedSize):
    cleanedURL = url.split("?")[0]
    return cleanedURL + "?size=" + str(requestedSize)


def getFileName(filename, RB, spoiler):
    if spoiler:
        return f"SPOILER_{filename}{getFileExtensionType(RB)}"
    else:
        return f"{filename}{getFileExtensionType(RB)}"


def getDefaultChannel(interaction: discord.Interaction):
    return getChannelFromID(interaction=interaction, channel_id=getDefaultReuploadChannel())
