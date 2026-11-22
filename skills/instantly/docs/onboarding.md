# Connect your Instantly account

Run onboarding with the file where you want to keep your settings. The default file is `.env`. A new file is readable and writable only by your local user. An existing file stays as it is.

```bash
instantly-api-tool --env-file 'work settings.env' onboarding
```

Open [Instantly settings](https://app.instantly.ai/app/settings/integrations), choose **API Keys**, and create a key with the permissions for the job. Copy it into your chosen file as `INSTANTLY_API_KEY`. Instantly shows the key once. Keep it out of chat and Git.

Onboarding prints the next command with the same settings file:

```bash
instantly-api-tool --output json --env-file 'work settings.env' auth check
```

This reads workspace details. It needs workspace read access. If your key is limited to campaigns, use `instantly-api-tool --env-file 'work settings.env' campaigns list --limit 10` to check that access directly. [Workspace API](https://developer.instantly.ai/api-reference/workspace/get-workspace)

## Settings

- `INSTANTLY_API_KEY` is the only value you need for the default connection. The CLI sends it as a bearer key.
- `INSTANTLY_API_BASE_URL` defaults to `https://api.instantly.ai/api/v2`.
- `INSTANTLY_TIMEOUT_S` defaults to 30 seconds.
- Values set in your shell take priority over values in the file. If the CLI uses a different key than you expected, check your shell settings.
- Write records normally go in `.state/runs/` next to the settings file. Keep the settings and run files private.

## If the check fails

- **401 or 403:** Check that you selected the right settings file and key. Check the permission for the command you ran.
- **429:** Instantly is asking you to slow down. Avoid tight loops and make fewer requests. Instantly documents workspace limits of 100 requests per 10 seconds and 600 per minute, with a separate limit of 20 per minute for listing emails. `emails list` returns up to 20 items by default. [Provider references](references.md)
- **Other errors:** Read the JSON error first. `--verbose` shows when a request starts and ends on stderr. `--debug` adds a Python traceback for local debugging. Before repeating a write after a lost reply, check the result and follow the [receipt instructions](safety_model.md#read-the-receipt).
