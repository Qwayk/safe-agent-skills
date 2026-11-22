---
name: statuspage
description: Check a public status page and summarize status, incidents, maintenance, and affected components.
---

# Check a public Statuspage

Use the public Statuspage URL the user gave you. If you do not know which page they mean, ask for its URL.

Run the command below for a current check. If the CLI is missing, use the Quickstart in the tool folder to install it.

```bash
statuspage-api-tool --output json --base-url https://status.atlassian.com summary get
```

Replace the example URL with the user’s page. Use `status get` if they only want the overall status. Use `incidents list` or `maintenances list` for recent history, including resolved incidents or completed maintenance.

Start the reply with what the page reports. Give the page URL and the check time. Include the names and times of open incidents or relevant maintenance, plus affected components when available. An empty list means the page showed no records in that list. When a read fails or the page leaves out details, tell the user what you could check.

Use this skill for public reads. For setup and exact flags, see the [Quickstart](docs/quickstart.md) and [Command guide](docs/command_reference.md).
