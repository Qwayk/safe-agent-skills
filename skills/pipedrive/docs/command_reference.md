# Pipedrive commands

Use [account setup](onboarding.md) to connect and [the quickstart](quickstart.md) for your first read.

## Common commands

```bash
qwayk-pipedrive-safe-agent-cli onboarding
qwayk-pipedrive-safe-agent-cli auth check
qwayk-pipedrive-safe-agent-cli users get-current
qwayk-pipedrive-safe-agent-cli deals list --limit 5
qwayk-pipedrive-safe-agent-cli goals search --type-name deals_won
qwayk-pipedrive-safe-agent-cli files download --id 12345
```

Run `qwayk-pipedrive-safe-agent-cli <group> <action> --help` for the exact flags. Find all shipped reads and exclusions in [API coverage](api_coverage.md). The file command returns [file details](safety_model.md#how-pipedrive-reads-work).

## Global flags

Use these before the command:

- `--env-file <path>` selects a settings file.
- `--config <path>` supplies JSON defaults for `base_url`, `api_domain`, and `timeout_s`.
- `--timeout-s <seconds>` changes how long each request waits.
- `--output json|text` selects the output format. JSON mode returns one object.
- `--log-file <path>` saves a local JSON audit log, one entry per line.
- `--verbose` shows HTTP request details. `--debug` shows Python errors.
- `--version` prints the installed version.

## Read more than one page

Lists default to one page. Use `--max-pages` on commands that support it. The maximum is 25 per command. Check `pagination.has_more` before treating a list as complete. When it is true, use the returned `pagination.next_cursor` as `--cursor` for cursor pages or `--start` for offset pages.

## Where the code lives

The Python package is in `src/qwayk_pipedrive_safe_agent_cli/`. Its `data/pipedrive_endpoint_catalog.json` lists the routes, `registry.py` loads it, and `cli.py` runs commands. `config.py` reads settings, `http.py` makes requests, and `output.py` and `errors.py` define replies.
