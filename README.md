# PM Attendance Tracker

Simple discord bot for meeting tracking for [Packmates Mutual Aid](https://packmatesaid.com/)

## Bot permissions
View channels, send messages (bitmask 3072) for now

## Developing
Run `uv run ruff check` and `uv run ruff format` before committing. Alternatively, use `cd .git/hooks && ln -sf ../../.github/scripts/pre-commit .` to install a precommit hook that does this for you.

For local testing, put a `BOT_TOKEN` env var in a local `.env` file, then `uv run --env-file .env pm-attendance-tracker`

For building and testing the docker image locally, do something like `docker build -t pm-attendance-tracker .` and `docker run -it --rm --env-file=.env pm-attendance-tracker`

For making a release, bump version number in `pyproject.toml` and run `uv lock`, add a changelog entry here, and push to github to make sure CI passes. After that, `git tag` it to the right version and push the tag to build and push the image to GHCR

## Todos
- implement tracking members in a spreadsheet (also think about permissions for starting meetings if we have this bot autoupdate spreadsheets. maybe for the meeting end message, there is a button in the modal that only admins can click on to track this meeting)
- fault tolerance for when bot has to be restarted during a meeting (keep track of state in local file? we will lose vc state regardless, this will be hard)

## Changelog

### 0.1.3
limit tracking commands to guild only

### 0.1.2
added meeting date and participant count to meeting summary, attach meeting summary as a file if it is too long, and fixed a logging f-string

### 0.1.1
Fix docker image build

### 0.1.0 (broken)
MVP, tracking functionality works (didn't exhaustively test for edge cases)
