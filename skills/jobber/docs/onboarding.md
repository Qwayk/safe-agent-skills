# Connect Jobber

Use an app from the Jobber Developer Center. An admin for the intended account approves it in Jobber. The app receives the authorization code and exchanges it for a token on its server. Keep codes, secrets and tokens out of chat, Git and shared logs. [Jobber authorization guide](https://developer.getjobber.com/docs/building_your_app/app_authorization/)

## Save app settings

Create a private `.env` file, or choose a file with `--env-file`. Settings in your shell take precedence over the file. When working with several accounts, use a separate folder for each so the tool picks its own token.

| Setting | What it does |
| --- | --- |
| `JOBBER_CLIENT_ID` and `JOBBER_CLIENT_SECRET` | Credentials from your app. Keep the secret on your computer or app server. |
| `JOBBER_REDIRECT_URI` | The exact address saved in Jobber for your app to receive the code. |
| `JOBBER_API_BASE_URL` | API address. Default `https://api.getjobber.com`. |
| `JOBBER_GRAPHQL_VERSION` | Version sent in the `X-JOBBER-GRAPHQL-VERSION` header. Default `2025-04-16` for this copy. |
| `JOBBER_TIMEOUT_S` | Request timeout. Default `30` seconds. |
| `JOBBER_API_TOKEN` | Optional token fallback. A token in `.state/token.json` beside the chosen settings file takes precedence. |

## Add the account token

1. Start approval through your app. The CLI's `auth authorize-url` command can build the link using your app settings. The app handles the returned code and exchanges it for tokens. Keep any URL with OAuth state out of saved logs.
2. Save the token JSON privately and import it. These commands use the same settings file for the import and the account check:

```bash
qwayk-jobber-safe-agent-cli --env-file account.env auth token set --file token.json
qwayk-jobber-safe-agent-cli --env-file account.env auth token status
qwayk-jobber-safe-agent-cli --env-file account.env auth check
qwayk-jobber-safe-agent-cli --env-file account.env read account --selection "id name"
```

Confirm the name and ID returned match the intended company before reading client records.

## Renew access

If the token has expired and renewal is approved, use the saved refresh token. Keep the app credentials available in your settings file or shell.

```bash
qwayk-jobber-safe-agent-cli --env-file account.env --apply --yes auth token refresh
```

Run `auth check` again after renewal. If Jobber rejects the refresh, check the app and account before starting a new authorization.

## If a check stops

- **Token missing.** Run `auth token status` with the intended `--env-file` and check whether you imported the token into that account's folder.
- **The account probe failed.** Check whether the token expired or the app lacks access.
- **Jobber rejected a request.** Read the error and check the named command and requested fields. If Jobber asks you to slow down, wait before trying another read.
- **A write was refused.** Review the plan and approval flags before trying again. [Review a change](safety_model.md)
- **Need more detail.** Use `--verbose` for request details or `--debug` for a stack trace. Remove any private values before sharing the output.
