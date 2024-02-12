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
from utils.utils import getChannelFromID, fetchUserFromID


async def sendFile(interaction: discord.Interaction, url, filename, channel, spoiler, source, sourcetype: str):
    returnedBytes = await downloadURL(url)
    if not checkFileSize(returnedBytes):
        await interaction.followup.send(f"### Failed Uploading file due to size limits by discord, details of upload are below.\n{source}\nOrigin URL: `{url}`\nHash: `{getHashOfBytes(returnedBytes.content)}` Size: `{getFileSize(returnedBytes.content)}", ephemeral=True)
        return
    hashOfBytes = getHashOfBytes(returnedBytes.content)
    if filename is None:
        filename = hashOfBytes
    finalFileName = getFileName(filename=filename, RB=returnedBytes, spoiler=spoiler)
    fileToSend = discord.File(io.BytesIO(returnedBytes.content), filename=finalFileName)
    if channel is None:
        channel = getDefaultChannel(interaction=interaction)
    # We Check if the URL is one of discord's links, and remove the extra bits before sending it out to the user.
    if "https://cdn.discordapp.com/attachments/" in url:
        url = url.split("?ex=")[0]

    if source != "":
        await channel.send(f"{source}\nOrigin URL: `{url}`\nHash: `{hashOfBytes}` Size: `{getFileSize(returnedBytes.content)}`", file=fileToSend)
        await interaction.followup.send(f"Successfully sent file!\n\nType: `{sourcetype}`\nSource: {source}", ephemeral=True)
    else:
        await channel.send(f"Origin URL: `{url}`\nHash: `{hashOfBytes}` Size: `{getFileSize(returnedBytes.content)}`", file=fileToSend)
        await interaction.followup.send(f"Successfully sent file!\n\nType: `{sourcetype}`", ephemeral=True)


async def sendAvatar(interaction: discord.Interaction, userID, channel, spoiler, source):
    discUser = await interaction.client.fetch_user(int(userID))
    userAvatarURL = discUser.avatar.url
    await sendFile(interaction=interaction, url=userAvatarURL, filename=discUser.id, channel=channel, spoiler=spoiler, source=source, sourcetype="Avatar")


async def sendBanner(interaction: discord.Interaction, userID, channel, spoiler, source):
    discUser = await interaction.client.fetch_user(int(userID))
    userBannerURL = adjustPictureSizeDiscord(discUser.banner.url, 1024)
    await sendFile(interaction=interaction, url=userBannerURL, filename=discUser.id, channel=channel, spoiler=spoiler, source=source, sourcetype="Banner")


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


async def formatSources(interaction: discord.Interaction, filename: str = None, source: str = None, userid: str = None):
    # If we have an userid, we first test for this, since it contains an early return in case of an improper user ID.
    formattedUsernames = None
    if userid is not None:
        discord_user = await fetchUserFromID(interaction, userid)
        if discord_user is None:
            return None  # Early return, and is handled in the function that called it.
        # We can safely get all the formatted usernames now.
        formattedUsernames = getFormattedUsernames(discord_user)

    # If we have a filename set, we set it, and continue.
    formattedFilename = None
    if filename is not None:
        formattedFilename = f"`{filename}`"

    formattedSource = None
    if source is not None:
        formattedSource = source

    # We put all of them together into a list, and then remove any None.
    formattedList = [formattedFilename, formattedUsernames, formattedSource]
    revisedList = list(filter(lambda item: item is not None, formattedList))

    # Finally we join the list together, if the list is empty, it just returns nothing, (but not none!)
    return " | ".join(revisedList).replace("\\n", chr(10))


def getDefaultChannel(interaction: discord.Interaction):
    return getChannelFromID(interaction=interaction, channel_id=getDefaultReuploadChannel())
