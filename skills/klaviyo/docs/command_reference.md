# Klaviyo commands

Start with the [quickstart](quickstart.md) if you want to list your audiences.

- `klaviyo-safe-agent-cli onboarding [--no-write-env]` creates or checks your local setup.
- `klaviyo-safe-agent-cli auth check` checks local settings. Put `--live` before `auth check` to check the account.
- `klaviyo-safe-agent-cli api ops list [--method GET|POST|PATCH|DELETE] [--tag <tag>]` lists commands.
- `klaviyo-safe-agent-cli api ops show --op <operation_command>` shows the required options for one command.
- `klaviyo-safe-agent-cli runs list [--limit 20]` finds recent runs.
- `klaviyo-safe-agent-cli runs show --run-id <id>` opens the summary for one run.

All 308 stable operations in the included April 2026 command list have an `api <operation_command>` command. See the [coverage table](api_coverage.md).

## Run a command

Put shared options, including `--env-file`, `--live`, `--apply`, and the approval flags, before `api`. Put operation inputs after the command name.

- Repeat `--path key=value` or `--query key=value` as needed.
- `--path-json`, `--query-json`, and `--body-json` take a JSON object or the path to a JSON file.
- Upload a file with `--file field=path`. Keep the same contents after reviewing the plan.
- Use `--artifacts-dir <path>` for a different local run folder, `--run-id <id>` to name the run, or `--no-artifacts` when you do not want automatic run files.

See [plans and receipts](safety_model.md) for write approvals and how to check a job.

## Where to find the code

`cli.py` reads options and saves command names in run history. `commands/api.py` checks plans, sends requests, and records results. `api_dispatch.py` builds the request plan. `config.py` reads settings, and `official_inventory.py` loads the saved command list.
