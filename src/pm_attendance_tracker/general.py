import discord
from discord.ext import commands


class PingTest(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=15)

    @discord.ui.button(
        label="Click me for interaction test", style=discord.ButtonStyle.green
    )
    async def test(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label = "Clicked"
        button.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == 400353271514136577

    async def on_timeout(self):
        self.children[0].label = "Timed out"
        self.children[0].disabled = True
        await self.edit_original_response(view=self)
        pass


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="ping",
        description="Ping test to make sure pm-attendance-tracker is online",
    )
    async def ping(self, interaction: discord.Interaction):
        view = PingTest()
        await interaction.response.send_message("Pong!", view=view)
