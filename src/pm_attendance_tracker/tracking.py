import logging
import datetime
import discord
from discord.ext import commands

# you must be in vc for 5 minutes to count as a participant
PARTICIPANT_VC_TIME_THRESHOLD = 300

logger = logging.getLogger(__name__)


class TrackedUser:
    def __init__(self, user, /, manual_checkin=False):
        self.user = user
        self.join_time = None
        self.total_time = datetime.timedelta()
        self.manual_checkin = manual_checkin

    def join(self):
        if self.join_time:
            logger.warning(
                f"processing user {self.user.id} joining meeting when we think they have already joined"
            )
            return
        self.join_time = datetime.datetime.now(datetime.UTC)
        logging.debug(f"user {self.user.id} joined")

    def leave(self):
        if not self.join_time:
            logger.warning(
                f"processing user {self.user.id} leaving meeting when we think they are not present"
            )
            return
        self.total_time += datetime.datetime.now(datetime.UTC) - self.join_time
        self.join_time = None
        logging.debug(f"user {self.user.id} left, total time {self.total_time}")

    def isActiveParticipant(self):
        return (
            self.manual_checkin
            or self.total_time.total_seconds() >= PARTICIPANT_VC_TIME_THRESHOLD
        )

    def __str__(self):
        return f"{self.user.display_name} ({self.user.name}) ({self.user.id})"


class TrackedVC:
    def __init__(self, vc, meeting_owner):
        self.vc = vc
        self.meeting_owner = meeting_owner
        self.users = {}
        self.start_time = datetime.datetime.now(datetime.UTC)

    def get_tracked_user(self, user):
        if user not in self.users:
            self.users[user] = TrackedUser(user)
        return self.users[user]

    def join(self, user):
        self.get_tracked_user(user).join()

    def leave(self, user):
        self.get_tracked_user(user).leave()

    def get_active_participants(self):
        return [u for u in self.users.values() if u.isActiveParticipant()]

    def get_summary_string(self):
        header = f"Meeting ran for: {str(datetime.datetime.now(datetime.UTC) - self.start_time)}\nParticipants:"
        return "\n".join([header] + [str(u) for u in self.get_active_participants()])


class Tracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracked_vcs = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None:
            if after.channel is None:
                logger.warning(
                    "a user has a voice status update but isn't in vc before or after? f{member} f{before} f{after}"
                )
                return
            vc = after.channel
            if vc in self.tracked_vcs:
                self.tracked_vcs[vc].join(member)
        else:
            if after.channel is not None:
                # just regular user-in-vc updates like mute/unmute, ignore
                return
            vc = before.channel
            if vc in self.tracked_vcs:
                self.tracked_vcs[vc].leave(member)

    @discord.app_commands.command(
        name="start-meeting", description="Start tracking attendees for a meeting"
    )
    async def start_meeting(self, interaction: discord.Interaction):
        user = interaction.user
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message(
                "ERROR: You must be in VC to do this action!"
            )
            return
        vc = user.voice.channel
        if vc in self.tracked_vcs:
            await interaction.response.send_message(
                "ERROR: This VC is already being tracked as part of a meeting!"
            )
            return
        logging.info(f"{user.id} started meeting for {vc.id}")
        self.tracked_vcs[vc] = TrackedVC(vc, user)
        for i in vc.members:
            self.tracked_vcs[vc].join(i)
        await interaction.response.send_message(
            f"Meeting started in VC channel <#{vc.id}>!"
        )

    @discord.app_commands.command(
        name="checkin",
        description="Check someone else into the current meeting manually",
    )
    async def checkin(
        self, interaction: discord.Interaction, checkin_member: discord.Member
    ):
        user = interaction.user
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message(
                "ERROR: You must be in VC to do this action!"
            )
            return
        vc = user.voice.channel
        if vc not in self.tracked_vcs:
            await interaction.response.send_message(
                "ERROR: This VC isn't being tracked as part of a meeting currently!"
            )
            return
        self.tracked_vcs[vc].users[checkin_member] = TrackedUser(
            checkin_member, manual_checkin=True
        )
        logging.info(
            f"{user.id} has checked in {checkin_member.id} manually for meeting {vc.id}"
        )
        if interaction.channel_id != vc.id:
            await vc.send(
                f"<@{user.id}> has checked in <@{checkin_member.id}> manually!"
            )
        await interaction.response.send_message(
            f"<@{user.id}> has checked in <@{checkin_member.id}> manually!"
        )

    @discord.app_commands.command(
        name="end-meeting", description="Stop a meeting and post the list of attendees"
    )
    async def end_meeting(self, interaction: discord.Interaction):
        user = interaction.user
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message(
                "ERROR: You must be in VC to do this action!"
            )
            return
        vc = user.voice.channel
        if vc not in self.tracked_vcs:
            await interaction.response.send_message(
                "ERROR: This VC isn't being tracked as part of a meeting currently!"
            )
            return
        logging.info(f"{user.id} ended meeting {vc.id}")
        for i in vc.members:
            self.tracked_vcs[vc].leave(i)
        await interaction.response.send_message(
            self.tracked_vcs[vc].get_summary_string()
        )
        del self.tracked_vcs[vc]
