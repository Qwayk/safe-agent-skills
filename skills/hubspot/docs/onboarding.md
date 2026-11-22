# Connect your HubSpot account

You can connect with a HubSpot private app token or an OAuth token file you already have. Keep the token on your computer and out of chat and Git.

## Use a private app token

1. Run `qwayk-hubspot-safe-agent-cli onboarding`. It creates a local `.env` if one is missing. From a source checkout it can copy `.env.example`.
2. In HubSpot, open **Settings → Integrations → Private apps**. Open or create a private app with the CRM permissions your work needs.
3. Set `HUBSPOT_ACCESS_TOKEN` in `.env` or in your shell. The older name `HUBSPOT_API_TOKEN` also works as a fallback.

## Use an existing OAuth token file

```bash
qwayk-hubspot-safe-agent-cli auth token set --file path/to/token.json
qwayk-hubspot-safe-agent-cli auth token status
```

The tool saves this file under `.state/token.json` next to your settings file. It uses the stored token when no configured token is present. If the token expires, renew it through your OAuth process and save the new token file with the same command.

## Check the connection

```bash
qwayk-hubspot-safe-agent-cli --output json auth check
```

This reads one owner from HubSpot. It checks that the token works for that read. Check permissions for the specific records or changes you need. Then run a small read and confirm the records are from the account you meant to use.

## Settings you can change

- Use `--env-file` before the command to select another settings file. Use the same flag for setup, auth checks, previews, and follow-up commands. Onboarding includes it in the next command it prints.
- Set `HUBSPOT_API_BASE_URL` only when you need a different API address. It defaults to `https://api.hubapi.com`. The older name `HUBSPOT_BASE_URL` also works.
- Requests wait up to 30 seconds by default. Set `HUBSPOT_TIMEOUT_S` or pass `--timeout-s` for one command.
- For the same setting name, a value in your shell takes precedence over the settings file.

## If a command fails

Check the settings file, account, token permissions, and record IDs. A missing owner permission can stop the connection check even if the token can read other records. Check the JSON result for the reason a command stopped. For a write whose result is unclear, check HubSpot before sending it again.

Use `--verbose` to see HTTP request details. Use `--debug` for a Python stack trace while working on the tool. Keep both kinds of output private if they contain account details. For a refused write, see [approval rules](safety_model.md).
