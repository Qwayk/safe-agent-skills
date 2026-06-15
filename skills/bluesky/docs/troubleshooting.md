# Troubleshooting

When Bluesky stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reading public posts, profiles, feeds, and social context, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Bluesky error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to print request timing to stderr.
Use `--debug` for full trace output.

Secrets are never printed.

## Auth checks

- If `auth check` says no session is active:
  - fill `BLUESKY_IDENTIFIER` and `BLUESKY_APP_PASSWORD`
  - run `bluesky-safe-cli auth login`
- If your app password is old, refresh auth:
  - run `bluesky-safe-cli auth refresh`
- To clear a bad local session:
  - run `bluesky-safe-cli auth logout`
- For token files:
  - run `bluesky-safe-cli auth token set --file token.json`
  - confirm with `bluesky-safe-cli auth token status`

## Apply refusals

Common reasons shown in tool output:
- `Refused: --live is required for apply`
- `Refused: --yes is required for risky operations`
- `Refused: --ack-irreversible is required for irreversible operations`

## API behaviors to remember

- Read commands run as dry-run plans until `--live`.
- Subscription commands return raw websocket frame captures in the receipt.
- Current write attempts require explicit no-snapshot approval before provider HTTP when no saved snapshot is available.
