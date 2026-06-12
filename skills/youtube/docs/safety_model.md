# How this skill stays safe

Use this page when you want to know what the YouTube skill can run right away, what needs review first, and which approvals matter before a real change.

## Safe by default

- API calls are plan-only by default.
- Live YouTube reads need explicit `--live`.
- `channels resolve` is also plan-only unless you add `--live`.
- `channels export --live` writes only local dataset files under `--out-dir`; it does not change YouTube state.
- Captions and other media downloads must use `--download-to` so binary data goes to a file, not into JSON output.
- Secrets are redacted from logs, JSON output, and audit artifacts.

## What needs extra approval

- Non-GET API calls start as dry-run plans first.
- Uploads start as dry-run plans first.
- Auth login and token-set flows start as dry-run plans first.
- Demo writes and write jobs also start as dry-run plans first.
- When there is no saved state to restore from, higher-risk actions need `--ack-no-snapshot` before the tool can try the write.
- Delete methods also need `--ack-irreversible`.

## What the approval flags mean

- `--live` means "run the real read or the approved local export now."
- `--apply --yes` means "I reviewed the plan and want the write attempt to continue."
- `--ack-no-snapshot` means "I understand there may be no saved state to restore from."
- `--ack-irreversible` means "I understand this delete or one-way action may not be reversible."

## What is still planning-only today

- `youtube-api-tool auth login --console` validates your OAuth setup and builds the plan, but it does not write `.state/token.json` yet.
- `youtube-api-tool auth token set --file token.json` also stops at the plan/refusal step today.

That means OAuth setup can still be inspected safely, but token writing is not automated by this build yet.

## Local file safety

- `channels export --live` refuses a non-empty output folder unless you choose `--overwrite`, `--yes`, or `--resume`.
- Downloads only write to the exact file path you give with `--download-to`.
- Local run history stays under `.state/runs/` so the proof is easy to inspect later.

## What proof it leaves behind

- Dry-run plans can be saved with `--plan-out`.
- Commands that really apply can save receipts with `--receipt-out` when the command supports it.
- Blocked apply attempts return a refusal that explains why nothing changed.
- Plans, refusals, receipts, and audit logs must stay secret-safe.

## The practical review loop

For anything risky, the expected flow is:

1. Generate the dry-run plan.
2. Review the channel, method, payload, file path, and risk.
3. Approve the exact live flags only if the plan still looks right.
4. Check the receipt or refusal so you know what really happened.
