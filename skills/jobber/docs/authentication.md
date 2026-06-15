# Authentication

Jobber authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For service-business clients, requests, jobs, quotes, invoices, and scheduling data, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Jobber credential path is configured, run the safe auth check, and stop before any token write or live account change."

## Authentication notes

Authentication means proving to Jobber that this tool can run the actions you requested.

## OAuth flow for this tool

1. In Jobber Developer Center, create or open your app.
2. Capture:
   - `JOBBER_CLIENT_ID`
   - `JOBBER_CLIENT_SECRET`
   - `JOBBER_REDIRECT_URI`
3. Create or refresh token JSON with the OAuth flow.
4. Store token JSON with:

```bash
qwayk-jobber-safe-agent-cli auth token set --file token.json
```

5. Confirm status:

```bash
qwayk-jobber-safe-agent-cli auth token status
```

6. Confirm account access:

```bash
qwayk-jobber-safe-agent-cli auth check
```

## Manual authorize URL helper

If your app needs an authorize URL first:

```bash
qwayk-jobber-safe-agent-cli auth authorize-url
```

You can add `--scope` and `--state` when required by your org process.

## Token refresh

Use refresh for token rotation maintenance:

```bash
qwayk-jobber-safe-agent-cli --apply --yes auth token refresh --refresh-token <refresh_token>
```

The tool can also use the stored token file if you omit `--refresh-token`.

## Safety notes

- Never paste access or refresh tokens in chat.
- `auth` helper output never includes token values.
- `.state/token.json` should stay local and private.
