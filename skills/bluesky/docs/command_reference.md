# Command reference

Use `bluesky-safe-cli`. It prints JSON by default. Use `--output text` for text. Put shared flags such as `--env-file`, `--live`, `--apply`, `--plan-in`, `--plan-out` and `--receipt-out` before the command.

## Setup and sign-in

```bash
bluesky-safe-cli onboarding
bluesky-safe-cli onboarding --no-write-env
bluesky-safe-cli auth login
bluesky-safe-cli auth check
bluesky-safe-cli auth refresh
bluesky-safe-cli auth logout
bluesky-safe-cli auth token set --file token.json
bluesky-safe-cli auth token status
```

See [account setup](onboarding.md) for what each command does and where session files are saved.

## Find and run a command

```bash
bluesky-safe-cli api ops list --kind query --docs-source http-reference
bluesky-safe-cli api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.social"}'
bluesky-safe-cli --live api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.social"}'
```

The command list accepts `--method GET|POST|WS`, `--namespace app.bsky|com.atproto|chat.bsky|tools.ozone`, `--kind query|procedure|subscription`, `--group`, `--docs-source http-reference|lexicon-only` and `--stability stable|unspecced|temp|active-development`.

Pass a JSON object or its file path to `--query-json` and `--body-json`. For simple fields, repeat `--query key=value` or `--body key=value`. Use `--input-file` and `--input-content-type` for binary requests. Use `--service-url` for a custom endpoint where the command uses it. Account-server routes use the saved or configured server. Public Bluesky queries without an access token use `BLUESKY_PUBLIC_API_URL`.

Subscriptions return raw WebSocket frames. Use `--event-limit` and `--idle-timeout-s` to control when the capture ends.

## Changes and local run history

Use [the post example](quickstart.md#publish-a-post) for a saved plan, an approved write and a separate read-back. The [safety guide](safety_model.md) explains the flags for other changes.

```bash
bluesky-safe-cli runs list --limit 20
bluesky-safe-cli runs show --run-id 2026-01-19T104512Z_a3f91c
```
