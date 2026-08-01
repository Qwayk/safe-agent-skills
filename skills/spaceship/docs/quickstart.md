# Quickstart

Your first result should be a read-only list of domains. Nothing in this guide changes the Spaceship account.

## Install the command

From the source folder:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install .
qwayk-spaceship-safe-agent-cli --output json --version
```

## Add account access

Copy `.env.example` to `.env`, then add only:

```text
SPACESHIP_API_KEY=<your key>
SPACESHIP_API_SECRET=<your secret>
```

The API host is fixed in the tool to `https://spaceship.dev/api`.

```bash
qwayk-spaceship-safe-agent-cli --output json auth check
```

`auth check` confirms that both local values exist. It does not call Spaceship.

## List domains without changing anything

```bash
qwayk-spaceship-safe-agent-cli --output json domains list --take 10
```

You should receive one JSON object with the result. Ask your agent to explain any domain that needs attention before moving to a write.

## Prepare a change without sending it

Write the official request body to `renewal.json`, then create a saved plan:

```bash
qwayk-spaceship-safe-agent-cli --output json \
  --run-id renewal-review \
  domains renew example.com \
  --body-file renewal.json
```

The plan is saved automatically at `.state/runs/renewal-review/plan.json`. Use `--plan-out renewal-plan.json` when you want a different path. A successful apply is saved the same way at `.state/runs/<run_id>/receipt.json` unless `--receipt-out` is supplied.

Keep `--run-id` to one simple local name like `renewal-review`. The tool refuses empty IDs, absolute paths, path separators, `.` and `..` before it creates a run folder.

Planning can run without credentials. Without credentials, the plan clearly says that no live snapshot or financial recheck was made and requires the stronger acknowledgement shown in `required_acknowledgements`.

Do not add `--apply` until the target, body digest, current-state check, risk labels, and required acknowledgements are correct. See the [safety model](safety_model.md) for the apply flow.

For sold-domain reports, `--take` defaults to 100 and cannot exceed 100. The official continuation field is `cursor`; optional filters are `--sale-date-time-from` and `--sale-date-time-to`.
