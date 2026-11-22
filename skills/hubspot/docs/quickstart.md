# Run your first HubSpot read

Ask your agent, “Show me ten HubSpot contacts with no owner so I can check them before we change anything.”

## Install and connect

If you are running the tool from a local checkout, use Python 3.12 or newer:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

Follow the [setup guide](onboarding.md), then check the connection:

```bash
qwayk-hubspot-safe-agent-cli auth check
```

## Start with a small read

```bash
qwayk-hubspot-safe-agent-cli hubspot objects list --object-type contacts --limit 10
qwayk-hubspot-safe-agent-cli hubspot objects search --object-type contacts --body-file search_body.json
```

The first command lists up to ten contacts. The second uses the filters in your own `search_body.json`. Ask the agent to explain what came back, flag missing fields or permissions, and show you enough to confirm it read the right account.

If you want to make a change, follow [the review steps](safety_model.md). See the [command guide](command_reference.md) for the exact options.
