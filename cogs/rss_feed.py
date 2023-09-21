"""
This file is a part of the module "RSS Feed"

All Files related to this module:
cogs/rss_feed.py
modules/rss_feeds/rss_feed_reader_utils.py
modules/rss_feeds/rss_feeds.json

If you do not want the rss feeds module, a future release will have a toggle within a config file. (otherwise just remove the files related to the module.)

This relies on the RSS feed having unique titles to find out what posts are older.
"""
import datetime
import random
from datetime import time

import discord
from discord import app_commands
from discord.ext import commands, tasks

from modules.rss_feeds.rss_feed_reader_utils import updateAllFeedsInteractions, updateAllFeedsAutoUpdate
from utils.bot_config import getMainGuildID
from utils.utils import getTime

# Changeable by the bot owner. It's by  the bot owner's timezone, so it runs once per hour of the owners timezone except for early hours.
# It starts at 8 AM, ends exactly on the next day, set with the below two lines. (appending 0 for the "first" hour of the day, 8 for 8 a.m., and 24 for all times between 0800 and 2300.)
# hours = list(range(8, 24))
hours = [0, 8, 16, 23]
# Below gets the dates ready for the bot to do its magic.
timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
times = []
for hour in hours:
    times.append(time(hour=hour, second=random.randrange(10, 15), tzinfo=timezone))
times.sort()


class RSS_Feeds(commands.Cog, name="RSS Feed Commands"):
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.fetchRSSFeeds.start()

    def cog_unload(self):
        self.fetchRSSFeeds.cancel()

    rss_feeds = app_commands.Group(name="rss", description="All RSS feed related commands", guild_ids=[getMainGuildID()])

    @rss_feeds.command(name="update-all", description="Updates all feeds")
    async def updateallfeeds(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await updateAllFeedsInteractions(interaction=interaction)

    @tasks.loop(time=times)
    async def fetchRSSFeeds(self):
        print(f"[{getTime()}] Fetching all feeds.")
        await updateAllFeedsAutoUpdate(self.bot)


async def setup(bot: discord.ext.commands.Bot):
    await bot.add_cog(RSS_Feeds(bot))
