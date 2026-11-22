# List your Instantly campaigns

Start by checking the account and reading a few campaigns. This shows which campaigns the key can see without changing their settings.

## Install the CLI

From the tool folder, run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
source .venv/bin/activate
instantly-api-tool --version
```

For local development, use `.venv/bin/python -m pip install -e '.[dev]'` from the tool folder.

## Connect and list campaigns

Run onboarding and use the local file it creates for your API key. Follow the connection command it prints. See [Onboarding](onboarding.md) if you use a different file or your key only has campaign access.

```bash
instantly-api-tool onboarding
instantly-api-tool auth check
instantly-api-tool campaigns list --limit 10
```

Read the campaign names and statuses, then ask the agent which campaign is worth checking first. If you want to change a campaign or its leads, ask for a preview first. [What you can ask for](use_cases.md) · [Approval rules](safety_model.md)
