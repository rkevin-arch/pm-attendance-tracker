import logging
import os

from pm_attendance_tracker.main import PMAttendanceTracker

logger = logging.getLogger(__name__)


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        logger.warning("BOT_TOKEN env var not present, reading token from token.txt")
        with open("token.txt") as f:
            token = f.read().strip()

    PMAttendanceTracker().run(token, root_logger=True)


if __name__ == "__main__":
    main()
