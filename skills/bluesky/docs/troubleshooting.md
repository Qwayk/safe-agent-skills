# Troubleshooting

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
