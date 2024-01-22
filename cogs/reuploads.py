"""
This file is a part of the module "Reuploads"

All Files related to this module:
cogs/reuploads.py
modules/reuploads/reuploads_utils.py
modules/reuploads/reuploads_config.py
modules/reuploads/reuploads_config.json

If you do not want the reuploads module, a future release will have a toggle within a config file. (otherwise just remove the files related to the module.)
"""

import discord
from discord import app_commands
from discord.ext import commands

from modules.reuploads.reuploads_config import setupReuploadsConfig
from utils.bot_config import getMainGuildID
from utils.files_utils import getHashOfBytes, downloadURL
from modules.reuploads.reuploads_utils import getFormattedUsernames, adjustPictureSizeDiscord, sendAvatar, sendBanner, sendFile, formatSources
from utils.utils import fetchUserFromID


class Reuploads(commands.Cog, name="Reuploads Commands"):
    def __init__(self, bot):
        self.bot = bot

    reuploads = app_commands.Group(name="reuploads", description="All reuploads related commands", guild_ids=[getMainGuildID()])

    @reuploads.command(name="info", description="Replies with info on the users features")
    @app_commands.describe(userid='ID of the User')
    async def info(self, interaction: discord.Interaction, userid: str):
        await interaction.response.defer(ephemeral=True)
        discord_user = await fetchUserFromID(interaction, userid)
        if discord_user is None:
            return
        if discord_user.avatar is None:
            await interaction.followup.send(f"User has no avatar for `{discord_user.id}`", ephemeral=True)
            return
        if discord_user.banner is None:
            userAvatarURL = discord_user.avatar.url
            await interaction.followup.send(f"Showing Info of {getFormattedUsernames(discord_user)}\n{userAvatarURL}", ephemeral=True, view=infoAvatar(discord_user.id))
        else:
            userAvatarURL = discord_user.avatar.url
            userBannerURL = adjustPictureSizeDiscord(discord_user.banner.url, 1024)
            await interaction.followup.send(f"Showing Info of {getFormattedUsernames(discord_user)}\n{userAvatarURL}\n{userBannerURL}", ephemeral=True, view=infoAvatarAndBanner(discord_user.id))

    @reuploads.command(name='upload', description='Upload Files')
    @app_commands.describe(channel='The channel to Send it in.')
    @app_commands.describe(filename='Name of the File')
    @app_commands.describe(url='Url of the Image')
    @app_commands.describe(spoiler='Whether or not the image should be hidden')
    @app_commands.describe(source='Sources which may include any text')
    @app_commands.describe(user_source='ID of a User, includes a mention, ID, username, and global name.')
    async def upload(self, interaction: discord.Interaction, url: str, filename: str = None, channel: discord.TextChannel = None, spoiler: bool = False, source: str = None, user_source: str = None):
        await interaction.response.defer(ephemeral=True)
        modifiedSource = await formatSources(interaction=interaction, filename=filename, source=source, userid=user_source)
        if modifiedSource is None:
            return
        await sendFile(interaction=interaction, url=url, filename=filename, spoiler=spoiler, channel=channel, source=modifiedSource, sourcetype="Upload")

    @reuploads.command(name='directupload', description='Directly replies & uploads Files')
    @app_commands.describe(filename='Name of the File')
    @app_commands.describe(url='Url of the Image')
    @app_commands.describe(spoiler='Whether or not the image should be hidden')
    @app_commands.describe(source='Sources which may include any text')
    async def upload(self, interaction: discord.Interaction, url: str, filename: str = None, spoiler: bool = False, source: str = None, user_source: str = None):
        await interaction.response.defer(ephemeral=True)
        modifiedSource = await formatSources(interaction=interaction, filename=filename, source=source, userid=user_source)
        if modifiedSource is None:
            return
        await sendFile(interaction=interaction, url=url, filename=filename, spoiler=spoiler, source=modifiedSource, channel=interaction.channel, sourcetype="Upload")

    @reuploads.command(name='avatar', description='Uploads Avatars')
    @app_commands.describe(channel='The channel to Send it in.')
    @app_commands.describe(userid='ID of the User')
    @app_commands.describe(spoiler='Whether or not the image should be hidden')
    @app_commands.describe(source='Sources which may include any text')
    async def avatar(self, interaction: discord.Interaction, userid: str, channel: discord.TextChannel = None, spoiler: bool = False, source: str = None):
        await interaction.response.defer(ephemeral=True)
        discord_user = await fetchUserFromID(interaction, userid)
        if discord_user is None:
            return
        if discord_user.avatar is None:
            await interaction.followup.send(f"User has no avatar for `{discord_user.id}`", ephemeral=True)
            return
        await sendAvatar(interaction=interaction, userID=userid, spoiler=spoiler, channel=channel, source=source)

    @reuploads.command(name='banner', description='Uploads Banners')
    @app_commands.describe(channel='The channel to Send it in.')
    @app_commands.describe(userid='ID of the User')
    @app_commands.describe(spoiler='Whether or not the image should be hidden')
    @app_commands.describe(source='Sources which may include any text')
    async def banner(self, interaction: discord.Interaction, userid: str, channel: discord.TextChannel = None, spoiler: bool = False, source: str = None):
        await interaction.response.defer(ephemeral=True)
        discord_user = await fetchUserFromID(interaction, userid)
        if discord_user is None:
            return
        if discord_user.banner is None:
            await interaction.followup.send(f"User has no banner for `{discord_user.id}`", ephemeral=True)
            return
        await sendBanner(interaction=interaction, userID=userid, spoiler=spoiler, channel=channel, source=source)


class infoAvatarAndBanner(discord.ui.View):
    def __init__(self, userID):
        super().__init__()
        self.userID = userID

    @discord.ui.button(label='Avatar', style=discord.ButtonStyle.primary)
    async def avatar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await sendAvatar(interaction=interaction, userID=self.userID, channel=None, spoiler=False, source=None)

    @discord.ui.button(label='Banner', style=discord.ButtonStyle.success)
    async def banner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await sendBanner(interaction=interaction, userID=self.userID, channel=None, spoiler=False, source=None)

    @discord.ui.button(label='Hash', style=discord.ButtonStyle.secondary)
    async def hash(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        discUser = await interaction.client.fetch_user(int(self.userID))
        returnedBytesAvatar = await downloadURL(discUser.avatar.url)
        returnedBytesBanner = await downloadURL(adjustPictureSizeDiscord(discUser.banner.url, 1024))
        await interaction.followup.send(f'Attached Hash for {self.userID}\nAvatar: `{getHashOfBytes(returnedBytesAvatar.content)}`\nBanner: `{getHashOfBytes(returnedBytesBanner.content)}`', ephemeral=True)


class infoAvatar(discord.ui.View):
    def __init__(self, userID):
        super().__init__()
        self.userID = userID

    @discord.ui.button(label='Avatar', style=discord.ButtonStyle.primary)
    async def avatar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await sendAvatar(interaction=interaction, userID=self.userID, channel=None, spoiler=False, source=None)

    @discord.ui.button(label='Hash', style=discord.ButtonStyle.secondary)
    async def hash(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        discUser = await interaction.client.fetch_user(int(self.userID))
        returnedBytes = await downloadURL(discUser.avatar.url)
        await interaction.followup.send(f'Attached Hash for {self.userID}\nAvatar: `{getHashOfBytes(returnedBytes.content)}`', ephemeral=True)


async def setup(bot):
    setupReuploadsConfig()
    await bot.add_cog(Reuploads(bot))
