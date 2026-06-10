# Proof pack (publish-ready evidence)

Purpose:
- Keep claims honest and checkable.
- Pair every behavior with a repeatable command path.
- Show what can go wrong and how to verify.

## Last verified

- Date (UTC): `2026-06-04`
- Tool version: `0.1.0`
- CLI name: `bluesky-safe-cli`
- Coverage source: `docs/api_coverage.md` (304 callable lexicons)

You do not need to run these commands yourself. They are here so the tool can be checked and audited.

## Smoke checks (run inside tool folder)

1) Version:
```bash
bluesky-safe-cli --output json --version
```

2) Auth check:
```bash
bluesky-safe-cli --output json auth check
```

3) Read preview (dry-run plan):
```bash
bluesky-safe-cli --output json api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.app"}'
```

4) Live read:
```bash
bluesky-safe-cli --output json --live api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.app"}'
```

5) Inventory-driven API list:
```bash
bluesky-safe-cli api ops list --method GET
```

## Evidence outputs

Committed examples:
- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (missing-approval refusal example; approved apply emits a receipt that records no-snapshot approval)

## What can go wrong

- **Auth fail**: use `auth login` first, then `auth check`.
- **Rate limit**: the error includes status and retry-safe behavior; no retry storm.
- **Plan gate fail**: ensure required `--apply`/`--live` and `--yes`/`--ack-irreversible` for risky writes.
- **Subscription output shape**: subscription calls return captured websocket frames, not fully decoded events.
- **Write verification**: current writes refuse with `before_state.status="blocked"` before provider HTTP.

## Coverage links

- `api_coverage.md` is the pinned surface:
  - 222 HTTP reference pages
  - 304 callable lexicons
  - 82 lexicon-only rows
