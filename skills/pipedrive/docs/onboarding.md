# Connect your Pipedrive account

Set your Pipedrive API token and either your company name or the full Pipedrive address. Keep the token out of chat, Git, and any files you share.

## Set up the connection

```bash
qwayk-pipedrive-safe-agent-cli onboarding
```

The command creates a settings file if one is missing. It copies a local `.env.example` when one is available. Otherwise it creates an empty file. Existing settings stay in place.

Put `PIPEDRIVE_API_TOKEN` in the settings file or your shell. Set `PIPEDRIVE_API_DOMAIN` to the company name from your Pipedrive address. The tool turns `my-company` into `https://my-company.pipedrive.com`. Use `PIPEDRIVE_BASE_URL` if you have a full address.

## Check the connection

Run the command onboarding prints, or run the default check:

```bash
qwayk-pipedrive-safe-agent-cli auth check
```

This calls `GET /api/v1/users/me`. Check that it returns the expected user before reading CRM data. Follow with a small read from the [quickstart](quickstart.md).

## Change local settings

- Use `--env-file` before the command to choose a different file. The default is `.env`.
- A value in your shell takes precedence over the same setting in the file. Use `--config` with a JSON file for defaults for `base_url`, `api_domain`, and `timeout_s`. Set the token in the shell or settings file.
- When both address settings have values, the full address takes precedence over the company name.
- Requests wait up to 30 seconds by default. Set `PIPEDRIVE_TIMEOUT_S` or pass `--timeout-s` for one command.

## If a command fails

Start with the chosen settings file, account address, and token. If the connection works but a read fails, check the record ID and the token’s permissions. In JSON output, `error` and `error_type` explain what stopped. Use `--verbose` for HTTP request details and `--debug` for a Python stack trace. Keep these logs private if they contain account details.
