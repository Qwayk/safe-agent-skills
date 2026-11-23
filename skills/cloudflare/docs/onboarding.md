# Connect your Cloudflare account

Create a Cloudflare API token with the access you need, save it in a private file on your machine, then check that the CLI reaches the right account.

## Create a token

Start with read access for the work you want. You can add permissions for a specific task later. Use Cloudflare’s [token setup guide](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/) and [guide to limiting token access](https://developers.cloudflare.com/fundamentals/api/how-to/restrict-tokens/).

For account and zone discovery, start with a token that can read those lists. For Workers inventory, give it access to the script, dispatch, KV metadata, builds or pipelines you need. D1 commands need access to D1. Browser Run needs the account permission `Browser Rendering - Edit`. The [approval guide](safety_model.md) explains which results must stay in local files.

## Save your settings

Run this from the folder where you want to keep your settings. The tool creates a private file:

```bash
cloudflare-api-tool --env-file .env onboarding
```

You can use `config init` for the same file setup without the follow-up command.

Fill in `CLOUDFLARE_API_TOKEN`. Set `CLOUDFLARE_ACCOUNT_ID` if you want the connection check to confirm the intended account. An older account-owned token without the `cfat_` prefix needs this setting so the CLI can tell it belongs to an account.

The CLI sends the token as a Bearer token. Keep the value in the private file and out of Git, chat and logs.

For a project with its own file, pass that file on every command. An explicit `--env-file` must point to an existing regular file. The CLI reads its Cloudflare settings from that file alone. With the default `.env` and no explicit flag, environment variables can override values in the file. This is useful in CI and containers.

### Optional settings

| Setting | When to use it |
| --- | --- |
| `CLOUDFLARE_API_BASE_URL` | Set a different API address. The default is `https://api.cloudflare.com/client/v4`. |
| `CLOUDFLARE_TIMEOUT_S` | Set the request timeout in seconds. The default is 30. |
| `CLOUDFLARE_CONNECT_TIMEOUT_S` | Set how long to wait for the connection. It defaults to the request timeout. |
| `CLOUDFLARE_READ_TIMEOUT_S` | Set how long to wait for the response. It defaults to the request timeout. |

For a slow endpoint, try `--timeout-profile slow` or set `--read-timeout-s`. Use `--progress` to see waiting messages. The CLI briefly caches some safe GET requests. Use `--no-cache` when you need a fresh result or `--cache-ttl-s` to set how long those results can be reused.

Private state defaults to `.state/` next to the selected file. `--project-dir` sets where commands can save protected output. Read the [command guide](command_reference.md#global-flags-selected) for the other options.

## Check the connection

```bash
cloudflare-api-tool --env-file .env --output json auth check
cloudflare-api-tool --env-file .env --output json accounts list
```

Start the account work when the check returns `ok=true` and you can identify the right account.

- An account-owned token starts with `cfat_` or is an older unprefixed token identified by the account ID in the selected file. The CLI checks it with `GET /accounts` and reports `verification=accounts_list`. When you set an account ID, confirm that `configured_account_match=true`.
- A `cfut_` user token, or an unprefixed token without an account ID, uses `GET /user/tokens/verify`. The token status must be `active`. An inactive token, empty account list or configured account mismatch returns `ok=false` and a nonzero exit code.
- When the task needs a particular Cloudflare feature, `auth probe --account-id <ACCOUNT_ID>` shows which common areas the token can reach. `auth probe` and `auth doctor` skip the user-token endpoint for account-owned tokens.

Use an explicit account ID for the current task. `accounts set-default` changes the saved local default. Before onboarding domains in bulk, run `auth zone-create-check` for the account.

## If a command stops

- **The file is missing, is a directory or has the wrong token.** Check the selected path and the values in that file. `config check` checks the local setup without calling Cloudflare. An invalid explicit path stops before the CLI calls Cloudflare.
- **`auth check` gets a 401 from `/user/tokens/verify`.** With an older account-owned token, check that the selected file names the intended account. If an account check also fails, read the exact error to see whether the token is invalid or lacks access.
- **The connection works but a product command fails.** Run the account-specific probe. For example, a D1 command can return an authentication error when the token works but is missing the D1 permission.
- **The command is slow or gets HTTP 429.** Use `auth doctor` to check how long the reads take. `--verbose` shows request start and end messages. If Cloudflare returns 429, reduce how often you make requests. Use `--debug` for a Python stack trace when debugging the CLI itself.
- **A write or file-only read was refused.** Keep the JSON error and check the target, approval, flags and output path. Review what happened before trying a write again. See [how approvals and saved results work](safety_model.md).
