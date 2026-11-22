# Command reference

Use the [offline quickstart](quickstart.md) to run commands from the source folder. The command names come from the [saved Reddit inventory](api_coverage.md).

- `api ops list` lists commands. Filter with `--section account`, `--method GET`, or `--scope submit`.
- `api <operation_command>` previews a request. Use `--path`, `--query`, and `--body` with `key=value` pairs. The JSON variants `--path-json`, `--query-json`, and `--body-json` accept JSON or a file. `--file field=/path/to/file` adds a file to the request and `--body-format` selects `form` or `json`.
- `onboarding --no-write-env`, `auth check`, and `auth token status` can inspect local setup without calling Reddit. See [old sign-in and settings](onboarding.md) to understand what they report.
- `runs list --limit 20` shows local run records. `runs show --run-id <run_id>` opens one. Runs are saved under `.state/runs/` unless you use `--no-artifacts`.
- `jobs run --file jobs.csv`, `demo read`, and `demo write --selector demo-resource` came from the shared tool template. They are outside the Reddit command list.

The [approval and recovery guide](safety_model.md) explains the flags and results you may see in old plans or receipts.
