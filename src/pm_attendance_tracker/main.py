import logging

import discord
from discord.ext import commands

from pm_attendance_tracker.general import General
from pm_attendance_tracker.tracking import Tracking

logging.basicConfig(level=logging.DEBUG)


class PMAttendanceTracker(commands.bot.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__("/", intents=intents)

    async def on_ready(self):
        await self.add_cog(General(self))
        await self.add_cog(Tracking(self))
        await self.tree.sync()
