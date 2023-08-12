"""
This file is a part of the module "RSS Feed"

All Files related to this module:
cogs/rss_feed.py
modules/rss_feeds/rss_feed_reader_utils.py
modules/rss_feeds/rss_feeds.json

If you do not want the rss feeds module, a future release will have a toggle within a config file. (otherwise just remove the files related to the module.)

This relies on the RSS feed having unique titles to find out what posts are older.
"""

import discord
from discord import app_commands
from discord.ext import commands

from modules.rss_feeds.rss_feed_reader_utils import updateAllFeeds
from utils.bot_config import getMainGuildID


class RSS_Feeds(commands.Cog, name="RSS Feed Commands"):
    def __init__(self, bot):
        self.bot = bot

    rss_feeds = app_commands.Group(name="rss", description="All RSS feed related commands", guild_ids=[getMainGuildID()])

    @rss_feeds.command(name="update-all", description="Updates all feeds")
    async def updateallfeeds(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await updateAllFeeds(interaction=interaction)


async def setup(bot):
    await bot.add_cog(RSS_Feeds(bot))
