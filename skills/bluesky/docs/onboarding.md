# Connect a Bluesky account

Public profiles and feeds are available without an account. Sign in when you need private account data or want to make an approved change.

## Sign in

1. Make an [app password in Bluesky settings](https://bsky.app/settings/app-passwords).
2. Run `bluesky-safe-cli --output json onboarding` to create a local `.env` file. Use `onboarding --no-write-env` to see what setup needs without creating a file.
3. Enter your handle or DID in `BLUESKY_IDENTIFIER` and the app password in `BLUESKY_APP_PASSWORD`. Keep both in the local file.
4. Run these commands to sign in and check the account.

```bash
bluesky-safe-cli --output json auth login
bluesky-safe-cli --output json auth check
```

`auth login` creates and saves the session. `auth check` reads the active session and shows the account and server. When the session expires, use `auth refresh` to renew it, or sign in again if the refresh token has expired. Use `auth logout` to clear the saved local session.

## Use separate accounts

Choose an account file with `--env-file /path/to/account/.env` before the command and use that choice for setup, sign-in and API calls. The state file is `.state/token.json` in the settings file's directory. Two settings files in the same directory share that state file. Use a separate directory for each account.

To use an existing local token file, run `bluesky-safe-cli auth token set --file token.json`. Use `auth token status` to check where it is saved. Keep settings and tokens out of chat and Git.

## Optional settings

Environment variables set by your shell take priority over the settings file. `BLUESKY_ACCESS_JWT` and `BLUESKY_REFRESH_JWT` supply existing session tokens. `BLUESKY_ADMIN_TOKEN` is for Ozone commands that need it.

| Setting | Default |
| --- | --- |
| `BLUESKY_PDS_URL` | Saved account server or the entryway |
| `BLUESKY_ENTRYWAY_URL` | `https://bsky.social` |
| `BLUESKY_PUBLIC_API_URL` | `https://public.api.bsky.app` |
| `BLUESKY_APPVIEW_URL` | `https://api.bsky.app` |
| `BLUESKY_CHAT_URL` | `https://api.bsky.chat` |
| `BLUESKY_OZONE_URL` | `https://mod.bsky.app` |
| `BLUESKY_LABELER_URL` | The Ozone URL |
| `BLUESKY_RELAY_URL` | `https://bsky.network` |
| `BLUESKY_TIMEOUT_S` | 30 seconds |

A saved account server takes priority over `BLUESKY_PDS_URL`. If setup fails, see [Troubleshooting](troubleshooting.md).
