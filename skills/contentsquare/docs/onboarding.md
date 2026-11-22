# Connect Contentsquare

Create server-to-server OAuth credentials in Contentsquare for the API you want to use. Keep the client secret and access tokens on your machine.

## Set up a private settings file

```bash
contentsquare-safe-cli onboarding
```

The command creates `.env` if it is missing. Only your user account can read and write a file created this way. To choose another file, put `--env-file` before the command:

```bash
contentsquare-safe-cli --env-file 'team settings.env' onboarding
```

Fill `CONTENTSQUARE_CLIENT_ID` and `CONTENTSQUARE_CLIENT_SECRET` in that file or set them in your shell. For account-level credentials, set `CONTENTSQUARE_PROJECT_ID` to the project you want to read. A project-level credential can use its assigned project. Shell settings take precedence over the settings file. The global `--oauth-project-id` flag selects the OAuth project for a single command.

Keep the file out of Git. Run `onboarding --no-write-env` if you only want to see what's missing.

| Setting | When to use it |
| --- | --- |
| `CONTENTSQUARE_AUTH_BASE_URL` | Leave it at `https://api.contentsquare.com` unless Contentsquare gives you a different OAuth address. |
| `CONTENTSQUARE_API_BASE_URL` | Leave it empty to use the API address from the token reply. Fill it only if Contentsquare gives you a fixed API address. |
| `CONTENTSQUARE_TIMEOUT_S` | The default is 30 seconds. Use `--timeout-s` to change it for one command. |

## Check the connection

Run the exact command onboarding gives you. For the default file, use:

```bash
contentsquare-safe-cli auth check
```

A successful check shows the requested or returned scope and the API address without printing the token. This confirms Contentsquare issued a token. Use the [first export read](quickstart.md#list-five-export-jobs) to check what that connection can see.

`auth check` asks for `data-export` by default. Normal commands choose `data-export`, `metrics`, `enrichment`, or `speed-analysis` based on the command. To check a different scope, use `auth check --scope metrics`, for example. Contentsquare requires `enrichment` to be used on its own. To check which projects and scopes a credential can use, run `contentsquare-safe-cli auth me`.

## If setup fails

- **Missing client ID or secret.** Use the same settings file for onboarding and the next command. Check that both values are set locally.
- **Wrong project or missing access.** Check the project ID, scope and permissions. For Enrichment, also confirm the integration ID. For a metrics read, check the date range.
- **Wrong API address.** Clear a custom `CONTENTSQUARE_API_BASE_URL` if Contentsquare supplies the address with the token.
- **A change stopped before sending.** Read the reason and check the [approval guide](safety_model.md).

Use the JSON error to explain what needs fixing. Keep credentials and exported data out of chat. Use `--verbose` for request details and `--debug` for a Python stack trace when debugging the CLI.
