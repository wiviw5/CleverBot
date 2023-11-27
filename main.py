import os

import discord
from discord.ext import commands

from cogs.minecraft_server import MCButtonView
from utils.bot_config import getMainGuildID
from utils.bot_secrets import getBotToken
from utils.utils import getTime, loadConfigs


class CleverBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self) -> None:
        self.add_dynamic_items(MCButtonView)

    async def on_ready(self):
        await load_cogs()
        print(f"Bot connected at: {getTime()} as {self.user} (ID: {self.user.id})")
        commands = await self.tree.fetch_commands(guild=discord.Object(getMainGuildID()))
        if len(commands) < 1:
            print(f"Manually resynced due to guild with ID {getMainGuildID()} having lost all commands.")
            await self.tree.sync(guild=discord.Object(getMainGuildID()))


bot = CleverBot()


async def load_cogs():
    print(f"Loading Cogs...")
    for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


async def unsync_commands():
    await bot.tree.sync()


loadConfigs()
bot.run(getBotToken())
