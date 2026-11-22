# Check Zapier and list apps

Set up the CLI and save the token with the [connection guide](onboarding.md). The commands below use `.env`. If you picked another file, pass `--env-file` before the command group.

```bash
qwayk-zapier-safe-agent-cli --output json auth check
qwayk-zapier-safe-agent-cli --output json partner get-v2-apps
```

The first command checks which profile the tool can read. The second shows the apps available to your integration. To review an existing Zap or action run, start with the matching read in the [command reference](command_reference.md).

If you already have White Label access and know the inbox ID, you can inspect its messages with `trigger-inbox listTriggerInboxMessages --inbox-id <value>`. Follow the [approval guide](safety_model.md) before leasing or acknowledging messages.

To prepare a change, start with the [saved-plan example](command_reference.md#prepare-one-change-at-a-time).
