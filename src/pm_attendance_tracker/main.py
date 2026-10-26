import discord
from discord.ext import commands

from pm_attendance_tracker.general import General
from pm_attendance_tracker.member_standing import MemberStanding
from pm_attendance_tracker.tracking import Tracking


class PMAttendanceTracker(commands.bot.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__("/", intents=intents)

    async def setup_hook(self):
        self.general = General(self)
        self.tracking = Tracking(self)
        self.member_standing = MemberStanding(self)
        await self.add_cog(self.general)
        await self.add_cog(self.tracking)
        await self.add_cog(self.member_standing)
        await self.tree.sync()
