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
import httpx

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
    if "https://cdn.discordapp.com/attachments/" in url or "https://cdn.discordapp.com/ephemeral-attachments/" in url:
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
        return f"`{discord_user.name.replace('`', '')}` | {discord_user.mention} | `{discord_user.id}`"
    # Finally, returning a properly formatted string at the end here.
    return f"`{discord_user.name.replace('`', '')}` | `{discord_user.global_name.replace('`', '')}` | {discord_user.mention} | `{discord_user.id}`"


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


async def handleTwitter(interaction: discord.Interaction, original_url: str, user_source: str):
    # Trimming off the start of the URL, no matter if its twitter or x, or the fixed links of those.
    trimmed_url = original_url.split("/")[3:]  # Removing the first 3 elements from the list.
    trimmed_url = "/".join(trimmed_url)  # Reforming the rest of the URL
    trimmed_url = trimmed_url.split("?")[0]  # Removing anything after the ? (normally tracking links, hopefully this causes no issues in the future with weird names)

    cleaned_url = "https://twitter.com/" + trimmed_url
    # Checking if it's a post, or just a profile check.
    api_url = "https://api.fxtwitter.com/" + trimmed_url
    rb: httpx.Response = await downloadURL(api_url)
    jsonOutput: dict = rb.json()

    # TODO, Implement URLS like BELOW
    # API DOCS: https://github.com/FixTweet/FxTwitter/wiki
    # Example URLS:
    # https://twitter.com/minikloon
    # https://x.com/minikloon
    # https://fxtwitter.com/minikloon
    # https://fixupx.com/minikloon
    # Example Tweet: https://twitter.com/Minikloon/status/1747663323716345881
    # Example API: https://api.fxtwitter.com/minikloon
    # Example API 2: https://api.fxtwitter.com/Minikloon/status/1747663323716345881
    # Example PFP 1: https://pbs.twimg.com/profile_images/626172982847774720/MbXX-auJ.png (Original Quality PFP)
    # Example PFP 2: https://pbs.twimg.com/profile_images/626172982847774720/MbXX-auJ_400x400.png (Zoomed Quality PFP)
    # Example PFP 3: https://pbs.twimg.com/profile_images/626172982847774720/MbXX-auJ_normal.png (Horrible Quality, This is returned from the API)
    # Example Banner 1: https://pbs.twimg.com/profile_banners/3392938462/1438127338 (Original Quality Banner, this is returned from the API)
    # https://devcommunity.x.com/t/retrieving-full-size-images-media-fields-url-points-to-resized-version/160494 For adjusting the Sizes of Images (both in posts, and the PFPs)
    # Example Image 1: https://pbs.twimg.com/media/GEDyeKOXIAAOhFw?format=jpg&name=orig (orig is original size)
    # Example Image 2: https://pbs.twimg.com/media/GEDyeKOXIAAOhFw?format=jpg&name=small (Default Image size)

    if "/status/" in api_url:
        mediaList: list = jsonOutput.get('tweet').get('media').get('all')
        authorName: str = jsonOutput.get('tweet').get('author').get("screen_name")
        authorLink: str = jsonOutput.get('tweet').get('author').get("url")

        if len(mediaList) == 1:
            mediaUrl = mediaList[0].get('url')
            modifiedSource = await formatSources(interaction=interaction,source=f"`{cleaned_url}` | `{authorLink}` | `{authorName}`", userid=user_source)
            if modifiedSource is None:
                return
            await sendFile(interaction=interaction, url=mediaUrl, filename=authorName, spoiler=False, channel=None, source=modifiedSource, sourcetype="Twitter Website Uploader")
            return

        linkList: list = []
        for media in mediaList:
            mediaUrl = media.get('url')
            if user_source is None:
                link: str = f"Media URL: {mediaUrl}\n```/reuploads upload url: {mediaUrl} source: `{cleaned_url}` | `{authorLink}` | `{authorName}` ```"
            else:
                link: str = f"Media URL: {mediaUrl}\n```/reuploads upload url: {mediaUrl} source: `{cleaned_url}` | `{authorLink}` | `{authorName}` user_source:{user_source} ```"
            linkList.append(link)

        links = "\n".join(linkList)

        await interaction.followup.send(f"Cleaned URL: `{cleaned_url}`\nUser URL: `{authorLink}`\nUsername: `{authorName}`\n{links}", ephemeral=True)
        # If it is a post, we need to show all the different pictures (Up to 4 pictures/gifs) on the post gotten from the fxtwitter api with buttons to upload them.
        # It'll also need to include a hash button.
    else:
        # If it is the Profile, we show the banner and Profile picture (If it doesn't have either, we let the user know) with buttons to upload them.
        # It'll also need to include a hash button.
        avatarUrl: str = jsonOutput.get('user').get('avatar_url').replace('_normal', '')
        bannerUrl: str = jsonOutput.get('user').get('banner_url')

        authorName: str = jsonOutput.get('user').get("screen_name")

        if user_source is None:
            avatarUploadCommand: str = f"```/reuploads upload url: {avatarUrl} source: `{cleaned_url}` | `{authorName}` ```"
            bannerUploadCommand: str = f"```/reuploads upload url: {bannerUrl} source: `{cleaned_url}` | `{authorName}` ```"
        else:
            avatarUploadCommand: str = f"```/reuploads upload url: {avatarUrl} source: `{cleaned_url}` | `{authorName}` user_source:{user_source} ```"
            bannerUploadCommand: str = f"```/reuploads upload url: {bannerUrl} source: `{cleaned_url}` | `{authorName}` user_source:{user_source} ```"

        uploadedString = ""
        if avatarUrl != "":
            uploadedString = uploadedString + f"\nAvatar: {avatarUrl}\n{avatarUploadCommand}"
        if bannerUrl != "":
            uploadedString = uploadedString + f"\nBanner: {bannerUrl}\n{bannerUploadCommand}"
        if uploadedString == "":
            uploadedString = "\nNo avatar or banner on user's profile."

        await interaction.followup.send(f"User URL: `{cleaned_url}`\nUsername: `{authorName}`{uploadedString}", ephemeral=True)


def getDefaultChannel(interaction: discord.Interaction):
    return getChannelFromID(interaction=interaction, channel_id=getDefaultReuploadChannel())
