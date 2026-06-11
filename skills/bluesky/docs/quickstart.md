# Quickstart

If you are non-technical, start with `docs/onboarding.md` and `docs/use_cases.md`.

This page is technical.

1) Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

2) Configure

```bash
cp .env.example .env
# fill BLUESKY_IDENTIFIER and BLUESKY_APP_PASSWORD
```

3) Run onboarding and login

```bash
bluesky-safe-cli onboarding
bluesky-safe-cli auth login
```

4) Smoke check

```bash
bluesky-safe-cli auth check
```

5) Read command flow

Dry-run preview:

```bash
bluesky-safe-cli api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.app"}'
```

Live read:

```bash
bluesky-safe-cli --live api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.app"}'
```

6) Write attempt flow (high-level)

```bash
bluesky-safe-cli --live --apply --yes api com-atproto-server-update-account-handle --body-json '{"account":"alice.bsky.app","handle":"alice.new.bsky.app"}'
```

If this is a risky write, add `--yes` and `--ack-irreversible` as needed.

Current write attempts are expected to require explicit no-snapshot approval before provider HTTP. Confirm `before_state.status="blocked"` and no receipt file was written.
