# Configuration

Most users need one private `.env` file:

```dotenv
ASANA_ACCESS_TOKEN=
ASANA_TIMEOUT_S=30
```

`ASANA_ACCESS_TOKEN` is required for provider reads and writes. `ASANA_TIMEOUT_S` is optional and must be greater than zero. An OS environment variable overrides the same key in `.env`.

Choose a different secret file with the global `--env-file PATH` flag. Global flags must come before the command:

```bash
asana-safe --env-file /private/path/asana.env --timeout-s 45 api get-workspaces
```

The production base URL is not configurable. Runtime requests are restricted to `https://app.asana.com/api/1.0`; tests inject a fake HTTP client instead of exposing a production URL override.

Generated local state is stored next to the selected env file:

- `.state/plans/PLAN_ID.json`
- `.state/receipts/PLAN_ID.json`
- `.state/plan-signing.key`

The signing key is a random 32-byte local HMAC-SHA256 key. It stays outside saved plans and is required to apply them. Do not copy it into chat, a plan, or a receipt. If it is lost or changed, create and review a new plan. Older unsigned or schema-1 plans are intentionally refused.

Choose another plan or receipt path with `--plan-out` or `--receipt-out`. Use `--log-file PATH` for an optional redacted JSONL audit log. New plans, receipts, signing keys, and audit logs are created atomically with mode `0600`; directories the tool creates use `0700`. Replacing an existing file never widens its permissions. `.env`, `.state`, virtual environments, caches, and build output are gitignored.
