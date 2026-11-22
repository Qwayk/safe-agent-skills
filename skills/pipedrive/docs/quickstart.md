# Run your first Pipedrive read

Ask your agent, “Show me five open deals so I can check them before we build the report.”

From a local checkout, install with Python 3.12 or newer:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install .
```

[Connect your account](onboarding.md), then check the user and list a few deals:

```bash
qwayk-pipedrive-safe-agent-cli auth check
qwayk-pipedrive-safe-agent-cli deals list --status open --limit 5
```

Confirm the user belongs to the right account. Ask the agent to show the deal names and stages and say whether there are more results. Check the [command guide](command_reference.md) for filters and pages.
