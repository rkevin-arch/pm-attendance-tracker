from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from pm_attendance_tracker.main import PMAttendanceTracker


class PingTest(discord.ui.View):
    def __init__(self, initial_interaction):
        super().__init__(timeout=15)
        self.initial_interaction = initial_interaction

    @discord.ui.button(
        label="Click me for interaction test", style=discord.ButtonStyle.green
    )
    async def test(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label = "Clicked"
        button.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == 400353271514136577

    async def on_timeout(self):
        button = self.children[0]
        if isinstance(button, discord.ui.Button):
            button.label = "Timed out"
            button.disabled = True
        await self.initial_interaction.edit_original_response(view=self)


class General(commands.Cog):
    def __init__(self, bot: PMAttendanceTracker):
        self.bot = bot

    @discord.app_commands.command(
        name="ping",
        description="Ping test to make sure pm-attendance-tracker is online",
    )
    async def ping(self, interaction: discord.Interaction):
        view = PingTest(interaction)
        await interaction.response.send_message("Pong!", view=view)
