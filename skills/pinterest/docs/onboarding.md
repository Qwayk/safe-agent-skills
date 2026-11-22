# Connect your Pinterest account

Use a private settings file. Pass `--env-file PATH` before the command when you use a file other than `.env`. Environment variables override values from that file. Keep settings, tokens, and sign-in codes out of chat and Git.

## Start with a read

Put a Pinterest access token in `PINTEREST_ACCESS_TOKEN` in your local settings file. The tool uses that token first. Leave out ads, catalog, and business permissions when you only need boards and pins. Start with `boards:read`, `pins:read`, and `user_accounts:read` for the account check.

```bash
pinterest-api-tool --env-file .env auth check
```

Check the username before working with boards or pins. [Pinterest’s sign-in guide](https://developers.pinterest.com/docs/getting-started/set-up-authentication-and-authorization/)

## Renew access

For ongoing access, set `PINTEREST_APP_ID` and `PINTEREST_APP_SECRET`. Use a saved token or put the initial refresh token in `PINTEREST_REFRESH_TOKEN`. Pinterest can return a new refresh token. The tool saves the new token for this settings file and uses it for the next renewal.

With an app that has the exact redirect address registered, you can sign in through your browser. This approved command saves local token state and updates the settings file.

```bash
pinterest-api-tool --env-file .env --yes --ack-no-snapshot auth login \
  --redirect-uri http://localhost:8765/ --continuous-refresh \
  --scopes boards:read,pins:read,user_accounts:read
```

For a sign-in code you already obtained, use `auth code exchange` with the registered redirect address and the same approval flags. Ask for permissions that match the job. Board changes need the relevant board write permission, and pin changes need `pins:write`. Pinterest can also limit features based on the app’s access.

## Bring over an existing token file

Each settings file now has its own token file. For `.env` it is `.state/pinterest/.env/token.json` next to the settings file. Run `auth token status` to see the path without showing token values. When a saved token can be renewed during a read, the tool may update that file.

If you used the old shared `.state/token.json`, first confirm which account it belongs to, then import it into the matching settings file. This copies the token into the new path.

```bash
pinterest-api-tool --env-file .env --yes --ack-no-snapshot auth token set --file .state/token.json
```

Then run `auth check` and confirm the username. The API defaults to `https://api.pinterest.com/v5` and the timeout defaults to 30 seconds. Use `PINTEREST_API_BASE_URL` or `PINTEREST_TIMEOUT_S` when those settings need to change.
