# Check your first public status page

If you already installed the agent skill, give it the public page URL and ask what is down, which incidents are open, and whether any maintenance is planned or active.

To use the CLI yourself, open the tool folder and run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/statuspage-api-tool --output json --base-url https://status.atlassian.com summary get
```

Read the overall status first. Then check the open incidents, planned or active maintenance, and any affected components the page lists. Include the page URL and the time of your check when sharing the result. For an incident or maintenance window, include the title and relevant times if the page supplies them.

For example, the [saved Atlassian result](examples/atlassian-summary.json) showed “All Systems Operational” and empty lists for incidents and maintenance. That file shows what a past check returned.

Use the [command guide](command_reference.md) to look up a recent resolved incident or completed maintenance. Use [setup and common errors](onboarding.md) to save your usual page or fix a failed request.
