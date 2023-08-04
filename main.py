import asyncio
import os

import discord
from discord.ext.commands import Bot

from utils.bot_config import getMainGuildID
from utils.bot_secrets import getBotToken
from utils.utils import getTime, loadConfigs

intents = discord.Intents.default()
bot = Bot(intents=intents, command_prefix="!")


async def load_cogs():
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


@bot.event
async def on_ready():
    print(f"Bot connected at: {getTime()} as {bot.user} (ID: {bot.user.id})")
    commands = await bot.tree.fetch_commands(guild=discord.Object(getMainGuildID()))
    if len(commands) < 1:
        print(f"Manually resynced due to guild with ID {getMainGuildID()} having lost all commands.")
        await bot.tree.sync(guild=discord.Object(getMainGuildID()))


async def unsync_commands():
    await bot.tree.sync()


loadConfigs()
asyncio.run(load_cogs())
bot.run(getBotToken())
