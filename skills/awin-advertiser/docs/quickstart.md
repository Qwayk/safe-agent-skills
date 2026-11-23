# Get your first Awin report

Start with “Which publishers drove the most sales last month?” Check the advertiser ID and the dates in the answer before using the results.

## Install the command

Run these commands from the folder containing `pyproject.toml`. Use Python 3.12 or newer.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/awin-advertiser-safe-cli --version
```

## Connect your account

```bash
.venv/bin/awin-advertiser-safe-cli --env-file .env onboarding
.venv/bin/awin-advertiser-safe-cli --env-file .env auth check
```

Open the file created by the first command. Add your API token and advertiser ID before running the second command. Check that it returns the advertiser ID you expected. [Setup and help](onboarding.md)

## Read a report

Replace `123456` and the dates with the advertiser ID and period you want to check.

```bash
.venv/bin/awin-advertiser-safe-cli --env-file .env reports publisher --advertiser-id 123456 --start-date 2026-06-01 --end-date 2026-06-30
```

Ask your agent to show the publishers that drove sales, the dates and account it used, and whether the result was empty or Awin returned an error.

[Find more commands](command_reference.md) · [Review a change before sending it](safety_model.md)
