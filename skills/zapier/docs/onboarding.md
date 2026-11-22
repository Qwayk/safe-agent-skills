# Connect to Zapier

Install the CLI from the [main guide](../README.md#install-and-first-run). Run onboarding from the folder where you want to keep your settings.

```bash
qwayk-zapier-safe-agent-cli --output json onboarding
```

Onboarding creates `.env` if it’s missing. The new file can only be read and edited by its owner. To use a different file, put `--env-file` before `onboarding`. Use `--no-write-env` to check setup without creating a file.

## Save the right credentials

For a Workflow API profile check, save your Zapier user access token as `ZAPIER_ACCESS_TOKEN`. Get it through your integration’s OAuth flow. Keep the token in your local settings and out of chat and Git. When it expires, refresh it through that same flow and replace the value in the file. [Zapier’s authentication guide](https://docs.zapier.com/powered-by-zapier/authentication/getting-started)

Some partner setups use credentials supplied by Zapier. The CLI reads a bearer access token first, then `ZAPIER_JWT`, then the pair `ZAPIER_CLIENT_ID` and `ZAPIER_CLIENT_SECRET`. Use the method Zapier gives you for the operation. For White Label access, follow Zapier’s token exchange and use the resulting access token for Trigger Inbox. Some promotions use a user token and others use an app token. [White Label token exchange](https://docs.zapier.com/white-label/implementation/token-exchange) · [Promotion enrollment](https://docs.zapier.com/powered-by-zapier/sponsor-user-automation/user-enrollment)

| Setting | What it does |
| --- | --- |
| `ZAPIER_BASE_URL` | Workflow and Promotions API address. Defaults to `https://api.zapier.com`. |
| `ZAPIER_TRIGGER_INBOX_BASE_URL` | Trigger Inbox address. Defaults to `ZAPIER_BASE_URL`. |
| `ZAPIER_TIMEOUT_S` | How many seconds the CLI waits for a reply. Defaults to 30. |

Use the default addresses unless Zapier gives your integration a different one. Settings in your shell take priority over values in the file.

## Check the connection

Run the `next_command` that onboarding prints. It uses the settings file you chose. With the default file, you can run this directly.

```bash
qwayk-zapier-safe-agent-cli --output json auth check
```

A successful reply shows the Zapier profile returned by the Workflow API. To check access to a different API, use a read command from that group with the right token. [Command reference](command_reference.md)

If the token is blank or expired, check the file you selected and replace the token. If Zapier rejects the request, check the token type, the permission for that operation, and whether your integration has Partner or White Label access. For account creation, follow [Zapier’s browser consent steps](https://docs.zapier.com/powered-by-zapier/zap-creation/quick-account-creation).
