# Architecture

The tool has a narrow path from an explicit CLI command to a provider request:

1. `cli.py` parses commands and shared safety flags.
2. `config.py` loads the selected env file and validates settings.
3. Named command handlers or the generated operation runner build a request plan.
4. `http.py` sends HTTP only when `--live` is present.
5. `output.py` emits one predictable JSON/text result; binary and sensitive payloads go to `--out`.
6. `plans.py`, `runs.py`, `json_files.py`, and `audit_log.py` retain local plan, receipt, and audit metadata without secrets.

The operation boundary is generated from `openapi.json`: 388 HTTP operations, of which 367 are stable implemented commands and 21 are deprecated. Seven manual WebSocket surfaces sit outside that HTTP count: six have plan-only commands, while the speech-engine upstream socket is callback-only. The developer-hosted Twilio initiation webhook is also callback-only, and one authentication row is docs-only.

Writes remain plan-first. If command-specific before-state capture is unavailable, the plan records `before_state.status: no_snapshot_available`; apply requires explicit `--ack-no-snapshot`, and the receipt records the recovery limit. A receipt is evidence of the CLI/provider response, not a promise of rollback or live success.
