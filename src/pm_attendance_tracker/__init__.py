import os
from pm_attendance_tracker.main import PMAttendanceTracker


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("BOT_TOKEN env var not present, reading token from token.txt")
        with open("token.txt") as f:
            token = f.read().strip()

    PMAttendanceTracker().run(token)


if __name__ == "__main__":
    main()
