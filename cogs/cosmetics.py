"""
This file is a crucial part of the bot, namely the management of cosmetic actions to make the server look good.
"""
import discord
from discord import app_commands
from discord.ext import commands

from utils.bot_config import getMainGuildID
from utils.utils import isOwner


class Cosmetics(commands.Cog, name="Management for Cosmetic management actions of the bot."):
    def __init__(self, bot):
        self.bot = bot

    cosmetics = app_commands.Group(name="cosmetics", description="All cosmetic management related commands", guild_ids=[getMainGuildID()])

    @cosmetics.command(name='editmessage', description='Edits a message')
    @app_commands.describe(messagelink='The link to the message you would like to edit.')
    @app_commands.describe(newmessage='The edits you would like to perform to the message.')
    async def editmessage(self, interaction: discord.Interaction, messagelink: str, newmessage: str):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        channelid = int(messagelink.split("/")[-2])
        messageid = int(messagelink.split("/")[-1])
        channel = await interaction.client.fetch_channel(channelid)
        message = await channel.fetch_message(messageid)
        await message.edit(content=newmessage.replace("\\n", chr(10)))
        await interaction.response.send_message(f"Attempted to edit the message at: {messagelink}", ephemeral=True)

    @cosmetics.command(name='getrawmessage', description='Replies with the raw text of a message.')
    @app_commands.describe(messagelink='The link to the message you would to get.')
    async def get_raw_message(self, interaction: discord.Interaction, messagelink: str):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        channelid = int(messagelink.split("/")[-2])
        messageid = int(messagelink.split("/")[-1])
        channel = await interaction.client.fetch_channel(channelid)
        message = await channel.fetch_message(messageid)
        await interaction.response.send_message(f"Here is the message if the link was valid!", ephemeral=True)
        await interaction.channel.send(content=message.content.replace(chr(10), "\\n"), view=deleteMessage())

    @cosmetics.command(name='sendmessage', description='Replies with the raw text in a new message.')
    @app_commands.describe(text='Replies with the text you send into the bot.')
    async def send_message(self, interaction: discord.Interaction, text: str):
        if not isOwner(interaction.user.id):
            await interaction.response.send_message(f"This command is not for public use!", ephemeral=True, delete_after=5)
            return
        await interaction.channel.send(content=text.replace("\\n", chr(10)))
        await interaction.response.send_message(f"Likely sent new message.", ephemeral=True)


class deleteMessage(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Delete', style=discord.ButtonStyle.danger)
    async def avatar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'Deleting Message...', ephemeral=True, delete_after=1)
        await interaction.message.delete()


async def setup(bot):
    await bot.add_cog(Cosmetics(bot))
