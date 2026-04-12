import discord
from discord.ext import commands
import asyncio

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ping", description="Ping test to make sure pm-attendance-tracker is online")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")
