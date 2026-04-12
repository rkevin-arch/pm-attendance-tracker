# PM Attendance Tracker

Simple discord bot for meeting tracking for [Packmates Mutual Aid](https://packmatesaid.com/)

## Bot permissions
View channels, send messages (bitmask 3072) for now

## Developing
Run `uv run ruff check` and `uv run ruff format` before committing

For local testing, put a `BOT_TOKEN` env var in a local `.env` file, then `uv run --env-file .env main.py`

For building and testing the docker image locally, do something like `docker build -t pm-attendance-tracker .` and `docker run -it --rm --env-file=.env pm-attendance-tracker`

## Todos
- implement tracking members in a spreadsheet (also think about permissions for starting meetings if we have this bot autoupdate spreadsheets)
- github actions for docker image building
- fault tolerance for when bot has to be restarted during a meeting (keep track of state in local file? we will lose vc state regardless, this will be hard)

## Changelog

### 0.1.0
MVP, tracking functionality works (didn't exhaustively test for edge cases)
