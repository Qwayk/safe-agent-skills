# Troubleshooting

When Qdrant Cloud stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent inspecting clusters, collections, keys, and vector database project data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Qdrant Cloud error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Live gate

If a command is refusing to call the API, make sure you added `--live`.

If a command is refusing to apply, check whether it requires:
- `--apply`
- `--yes`
- `--ack-irreversible` (DELETE-like)
- `--ack-spend-money` (payment/billing)
- `--plan-in` (high-risk applies)
