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

    @discord.app_commands.command(
        name="check-meeting-standing",
        description="Check if everyone in a meeting is in good standing. Useful for deciding to speed up meetings",
    )
    @discord.app_commands.guild_only
    async def check_meeting_standing(self, interaction: discord.Interaction):
        user = interaction.user
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message(
                "ERROR: You must be in VC to do this action!", ephemeral=True
            )
            return
        vc = user.voice.channel
        tracked_vc = self.bot.get_cog("Tracking").tracked_vcs.get(vc)
        if not tracked_vc:
            await interaction.response.send_message(
                "ERROR: This VC isn't being tracked as part of a meeting currently!",
                ephemeral=True,
            )
            return

        # this should include anyone in the vc currently, anyone who left but counts as participated, and anyone manually checked in
        current_users = set(
            vc.members + [u.user for u in tracked_vc.get_active_participants()]
        )
        good_standing_users = 0
        not_good_standing_summary = []
        for user in current_users:
            if user.id in self.good_standing_members:
                good_standing_users += 1
                continue
            joined_meetings = sum(
                (1 for i in self.active_meetings if user.id in i["participant_ids"])
            )
            not_good_standing_summary.append(
                f"- <@{user.id}> (joined {joined_meetings}/{len(self.active_meetings)} meetings)"
            )

        result = [
            f"{good_standing_users}/{len(current_users)} participant(s) are in good standing."
        ]
        print(current_users, good_standing_users, not_good_standing_summary)
        if len(not_good_standing_summary) == 0:
            result.append("Everyone present is in good standing!")
        else:
            result.append("The following participant(s) are not in good standing:")
            result += not_good_standing_summary[:15]
            if len(not_good_standing_summary) > 15:
                result.append(f"- ... and {len(not_good_standing_summary) - 15} more")

        await interaction.response.send_message("\n".join(result))
