# Statuspage

Check a vendor’s public status page before you deploy or reply to a customer. Ask your agent to show the overall status, open incidents, planned or active maintenance, and any affected components the page names. You only need the public Statuspage URL.

## Install and try it

Ask your agent to install the `statuspage` skill from `Qwayk/safe-agent-skills`, or run:

```bash
npx skills add Qwayk/safe-agent-skills@statuspage -g -y
```

If the skill is missing from the list, reopen your agent app or attach the skill to the workspace if your app requires it.

> Check https://status.atlassian.com. Tell me what’s down, which incidents are open, and whether maintenance is planned or underway.

Use the [Quickstart](docs/quickstart.md) to run the command yourself. The [setup guide](docs/onboarding.md) explains how to save a default page and fix common errors.

The skill reads public pages served by Statuspage. Each answer reflects what that page reports. If you need to tell whether a problem is on your side, check your own service too.

- [Command guide](docs/command_reference.md)
- [All Statuspage docs](docs/README.md)
