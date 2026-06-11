# API coverage

Last audited/verified (UTC): 2026-06-01T00:00:00Z

This tool targets Plausible Analytics.

## Coverage definition (canonical inventory)

Coverage is defined against the official Plausible API documentation listed in `docs/references.md`:
- Stats API v2
- Events API
- Sites API v1

Additionally, this tool includes the `GET /api/health` endpoint used for basic availability checks.

This ledger is considered “complete” when every in-scope endpoint from that canonical inventory appears as a row and is mapped to a named CLI command.

Out of scope: Plausible UI-only features, billing/account/admin, and any undocumented or enterprise-only endpoints not covered by the official docs above.

Staleness clause: if the upstream Plausible docs change, this ledger must be re-audited and the timestamp above must be updated.

Legend:
- ✅ implemented
- ❌ not implemented

## Notes

- This tool focuses on safe, deterministic workflows: plan → review → apply → (best-effort) verify.
- In `--output json` mode, every invocation prints exactly one JSON object.
- Endpoint details and official docs links live in `docs/references.md`.
- Write plans now include `plan.recovery`, and apply receipts now include `receipt.recovery`.
- This tool currently uses only `irreversible_and_clearly_labeled` and `rollback_by_inverse_action`.
- `site goals ensure`, `site goals delete`, `site custom-props ensure`, `site custom-props delete`, `site guests ensure`, and `site guests delete` include persisted `before_state` and `before_state_path` where possible.
- `event send` and `site shared-links ensure` remain without persisted before-state because this CLI cannot read the same exact prior state needed for those writes.

## Ledger (complete for scoped inventory)

Each row is intended to be specific enough to implement and test without re-reading the upstream docs.

### Health (read-only)

| Method | Path | Purpose | CLI | Safety | Verification | Tests |
|---|---|---|---|---|---|---|
| GET | `/api/health` | Basic availability check | `auth check` | Read-only | N/A | `tests/test_smoke.py` (construction); `auth` behavior covered via CLI contract tests |

### Stats API v2 (read-only)

| Method | Path | Purpose | CLI | Safety | Verification | Tests |
|---|---|---|---|---|---|---|
| POST | `/api/v2/query` | Run Stats API v2 queries | `stats query` | Read-only | Response returned as-is | `tests/test_stats_commands.py`, `tests/test_cli_stats_validate_roundtrip.py` |

### Events API (write; irreversible)

| Method | Path | Purpose | CLI | Safety | Verification | Tests |
|---|---|---|---|---|---|---|
| POST | `/api/event` | Send an analytics event | `event send` | Dry-run by default; apply requires `--apply --yes --ack-irreversible --ack-no-snapshot` | Best-effort Stats API poll on a unique URL path when `--verify` is requested | `tests/test_event_safety.py` |

#### `event send` payload fields (supported)

Required:
- `domain` (defaults to `PLAUSIBLE_SITE_ID`)
- `name`
- `url`

Optional:
- `props` (key/value map; refused/redacted if likely-PII)
- `interactive` (boolean)
- `referrer` (URL; refused if likely-PII)
- `revenue` (`{"currency":"USD","amount":"9.99"}`; both required together if used)

Explicit refusals (by design):
- IP injection / `X-Forwarded-For` / custom client IP: not supported (PII risk); no CLI flags exist for this.

### Sites API v1 (reads + safe writes)

| Method | Path | Purpose | CLI | Safety | Verification | Tests |
|---|---|---|---|---|---|---|
| GET | `/api/v1/sites` | List sites | `site list` | Read-only | N/A | `tests/test_sites_commands.py` |
| GET | `/api/v1/sites/teams` | List teams | `site teams list` | Read-only | N/A | `tests/test_sites_commands.py` |
| GET | `/api/v1/sites/:site_id` | Get site details | `site get [--site-id]` | Read-only | N/A | `tests/test_sites_commands.py` |
| POST | `/api/v1/sites` | Create site | `site create` | Default refused without `--apply`; apply requires `--apply --yes` | Read-back: `GET /api/v1/sites/:site_id` | `tests/test_sites_commands.py` |
| PUT | `/api/v1/sites/:site_id` | Update site (domain and/or tracker config) | `site update` | Default refused without `--apply`; apply requires `--apply --yes` | Read-back: `GET /api/v1/sites/:site_id` (new domain if changed) | `tests/test_sites_commands.py` |
| DELETE | `/api/v1/sites/:site_id` | Delete site (destructive) | `site delete` | Default refused without `--apply`; apply requires `--apply --yes --ack-irreversible` | Best-effort: confirm removed from `GET /api/v1/sites` | `tests/test_sites_commands.py` |
| PUT | `/api/v1/sites/shared-links` | Find-or-create shared link (idempotent) | `site shared-links ensure` | Dry-run by default; apply requires `--apply --yes --ack-no-snapshot` | Read-back: repeat PUT (idempotent) | `tests/test_sites_commands.py` |
| GET | `/api/v1/sites/goals` | List goals | `site goals list` | Read-only | N/A | `tests/test_sites_commands.py` |
| PUT | `/api/v1/sites/goals` | Find-or-create goal (idempotent) | `site goals ensure` | Default refused without `--apply`; apply requires `--apply --yes` | Read-back: `GET /api/v1/sites/goals` and match `id`/`display_name` | `tests/test_sites_commands.py` |
| DELETE | `/api/v1/sites/goals/:goal_id` | Delete goal (destructive) | `site goals delete` | Default refused without `--apply`; apply requires `--apply --yes --ack-irreversible` | Best-effort: `GET /api/v1/sites/goals` and confirm missing | `tests/test_sites_commands.py` |
| GET | `/api/v1/sites/custom-props` | List custom properties | `site custom-props list` | Read-only | N/A | `tests/test_sites_commands.py` |
| PUT | `/api/v1/sites/custom-props` | Create custom property (idempotent) | `site custom-props ensure` | Default refused without `--apply`; apply requires `--apply --yes` | Read-back: `GET /api/v1/sites/custom-props` and confirm present | `tests/test_sites_commands.py` |
| DELETE | `/api/v1/sites/custom-props/:property` | Delete custom property (destructive) | `site custom-props delete` | Default refused without `--apply`; apply requires `--apply --yes --ack-irreversible` | Best-effort: `GET /api/v1/sites/custom-props` and confirm missing | `tests/test_sites_commands.py` |
| GET | `/api/v1/sites/guests` | List guests | `site guests list` | Read-only | N/A | `tests/test_sites_commands.py` |
| PUT | `/api/v1/sites/guests` | Invite/add guest (idempotent) | `site guests ensure` | Default refused without `--apply`; apply requires `--apply --yes` | Read-back: `GET /api/v1/sites/guests` and confirm email present | `tests/test_sites_commands.py` |
| DELETE | `/api/v1/sites/guests/:email` | Remove guest/invite (destructive) | `site guests delete` | Default refused without `--apply`; apply requires `--apply --yes --ack-irreversible` | Best-effort: `GET /api/v1/sites/guests` and confirm missing | `tests/test_sites_commands.py` |
