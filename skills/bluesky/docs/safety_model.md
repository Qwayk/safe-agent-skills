# Safety model

This tool is built to slow Bluesky changes down before they go live.

## What this tool does by default

- API calls preview first as dry-run plans.
- Live reads need `--live`.
- Live writes need `--live --apply`.
- Secrets stay redacted in normal output and logs.

## Where the extra caution happens

Some Bluesky writes do not have a saved before-state or a real rollback path.

When that happens:

- the plan must disclose the no-snapshot limit
- live apply needs `--ack-no-snapshot`
- risky writes can also need `--yes`
- irreversible writes can also need `--ack-irreversible`

If the needed approval is missing, the tool should refuse before provider HTTP.

## Recommended workflow

1. Run auth and one small live read first.
2. Preview the exact write plan.
3. Review the endpoint, payload, target account, and recovery limits.
4. Apply only with the required live and approval flags.
5. Review the refusal or receipt after the run.

## Plans, receipts, and run history

- `--plan-out <path>` saves a dry-run plan.
- `--receipt-out <path>` saves an apply receipt when the write is approved and runs.
- `runs list` and `runs show` help inspect local run history.

These files are the proof trail for what the tool planned, what it refused, and what it actually ran.

## Limits

- Many Bluesky write families should still be treated as irreversible.
- This tool does not promise rollback, backup, or restore helpers for those writes.
- Subscription output is raw frame capture, not a polished decoded event view.
