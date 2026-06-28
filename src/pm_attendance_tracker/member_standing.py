import discord
import yaml
import logging
import os
import pathlib
import collections
from discord.ext import commands
from typing import Optional

logger = logging.getLogger(__name__)


class MemberStanding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        try:
            self.reload_meetings()
            logger.info(
                f"Member standing DB loaded with {len(self.good_standing_members)} in good standing."
            )
        except Exception as e:
            logger.warning(
                "Loading past meeting info has failed! Member standing DB will be initialized to empty"
            )
            logger.exception(e)
            self.active_meetings = []
            self.good_standing_members = []

    def reload_meetings(self):
        # kinda playing it fast and loose with data validation
        # fine for now cuz it's just me doing this, but to be improved in the future
        all_meetings = []
        db_dir = pathlib.Path(os.environ["MEETING_DB_DIR"])
        for file in db_dir.glob("*.yaml"):
            with file.open() as f:
                all_meetings.append(yaml.safe_load(f))
        assert all(x["pmat_meeting_version"] == 1 for x in all_meetings)

        all_meetings.sort(key=lambda x: x["date"], reverse=True)
        active_meetings = all_meetings[:12]

        member_counter = collections.Counter()
        for meeting in active_meetings:
            member_counter.update(meeting["participant_ids"])
        good_standing_members = [k for k, v in member_counter.items() if v >= 3]

        self.active_meetings = active_meetings
        self.good_standing_members = good_standing_members

    @discord.app_commands.command(
        name="reload-meeting-db",
        description="Reload meeting database. You shouldn't need this unless you are the bot owner, but it's safe to run!",
    )
    @discord.app_commands.guild_only
    async def reload_meeting_db(self, interaction: discord.Interaction):
        try:
            self.reload_meetings()
            await interaction.response.send_message(
                f"Done! We now have {len(self.good_standing_members)} members in good standing.",
                ephemeral=True,
            )
        except Exception as e:
            logger.warning("Reloading past meeting info has failed!")
            logger.exception(e)
            await interaction.response.send_message(
                "Reload has failed! Check logs for details.", ephemeral=True
            )

    @discord.app_commands.command(
        name="standing",
        description="Check if a member is in good standing. Leave the member blank to check yourself.",
    )
    @discord.app_commands.guild_only
    async def standing(
        self, interaction: discord.Interaction, member: Optional[discord.Member]
    ):
        if member is None:
            member = interaction.user
        joined_meetings = [
            i for i in self.active_meetings if member.id in i["participant_ids"]
        ]
        message = "\n".join(
            [
                f"<@{member.id}> "
                + (
                    "is in **GOOD STANDING**."
                    if member.id in self.good_standing_members
                    else "**IS NOT** in good standing."
                ),
                f"<@{member.id}> has joined {len(joined_meetings)} out of the past {len(self.active_meetings)} general meetings, listed below.",
            ]
            + [f"- {i['date']}" for i in joined_meetings]
        )
        await interaction.response.send_message(message, ephemeral=True)
