# Authentication

Authentication means proving to Jobber that this tool can run the actions you requested.

This tool uses OAuth 2.0 in the common case.

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
