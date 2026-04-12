import os
import asyncio
import logging

import discord
from discord.ext import commands

from general import General

logging.basicConfig(level=logging.DEBUG)

class PMAttendanceTracker(commands.bot.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__("/", intents=intents)

    async def on_ready(self):
        await self.add_cog(General(self))
        await self.tree.sync()

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("BOT_TOKEN env var not present, reading token from token.txt")
        with open("token.txt") as f:
            token = f.read().strip()

    PMAttendanceTracker().run(token)

if __name__ == "__main__":
    main()
