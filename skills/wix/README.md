# Wix

Find the Wix site you want to work on, then check its store catalog, bookings, or contacts. For example, ask your agent to list the sites in your account and check which catalog your store uses.

The agent starts by confirming the account or site. Before it edits a product or publishes a site, it shows the exact change and asks you to approve the saved plan. The receipt tells you what Wix accepted and what the tool could check afterward.

## Install and start

Ask your agent to install the Wix skill from Qwayk, or run:

~~~bash
npx skills add Qwayk/safe-agent-skills@wix -g -y
~~~

Use [Quickstart](docs/quickstart.md) to install the command and make your first check. Use [Connect Wix](docs/onboarding.md) to choose between an account key for listing sites and an app connection for work on one site.

## What you can ask

- “Show me the sites in this account. Give me their names and IDs.”
- “Check which catalog version this store uses. If it uses V3, show me a few products.”
- “Show me exactly which product fields would change. Wait for my approval.”
- “Check which site would be published. After I approve, tell me what Wix confirmed and which page I should check.”

The tool uses Wix’s documented API methods. Your key or app needs access to the site and permission for the action. Editing the layout or content in Wix Editor happens in Wix Editor. A publish receipt reports the site’s status, and the public page shows whether the intended edits are visible.

For more, see [Commands](docs/command_reference.md), [Approvals and receipts](docs/safety_model.md), [API coverage](docs/api_coverage.md), and [What we tested](docs/proof.md).
