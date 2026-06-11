# Quickstart

Want the short non-technical path first? Start with [What you can do with Bluesky](use_cases.md), [Connect your Bluesky account](onboarding.md), and [How this skill stays safe](safety_model.md).

This page is for the exact commands.

## 1) Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## 2) Configure

```bash
cp .env.example .env
```

Fill:

- `BLUESKY_IDENTIFIER`
- `BLUESKY_APP_PASSWORD`

## 3) Log in and check auth

```bash
bluesky-safe-cli --output json onboarding
bluesky-safe-cli --output json auth login
bluesky-safe-cli --output json auth check
```

## 4) First safe reads

Preview the read first:

```bash
bluesky-safe-cli --output json api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.social"}'
```

Then run the live read:

```bash
bluesky-safe-cli --output json --live api app-bsky-actor-get-profile --query-json '{"actor":"alice.bsky.social"}'
```

## 5) Operation inventory

List the available documented operations before choosing one:

```bash
bluesky-safe-cli --output json api ops list --kind query
```

## 6) Write preview and apply flow

Write preview:

```bash
bluesky-safe-cli --output json api com-atproto-repo-create-record --body-json '{"repo":"did:plc:example","collection":"app.bsky.feed.post","record":{"$type":"app.bsky.feed.post","text":"Hello from a preview"}}'
```

Approved live apply:

```bash
bluesky-safe-cli --output json --live --apply --ack-no-snapshot api com-atproto-repo-create-record --body-json '{"repo":"did:plc:example","collection":"app.bsky.feed.post","record":{"$type":"app.bsky.feed.post","text":"Hello from a reviewed apply"}}'
```

Add `--yes` for risky writes and `--ack-irreversible` when the action is labeled irreversible.
