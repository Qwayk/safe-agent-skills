# Run your first Salesforce read

Ask your agent, “Check my Salesforce connection and show me five accounts.”

From a local checkout, install with Python 3.12 or newer:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install .
```

Follow [account setup](onboarding.md), then run a small read:

```bash
qwayk-salesforce-platform-safe-agent-cli --output json auth check
qwayk-salesforce-platform-safe-agent-cli --output json query run --soql "SELECT Id, Name FROM Account LIMIT 5"
```

Check that this is the right Salesforce org. Ask the agent to summarize what it found and say when permissions or limits affect the result. If you want to make a change, follow the [approval steps](safety_model.md).
