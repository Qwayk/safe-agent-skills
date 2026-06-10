# Quickstart

If you are non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is a technical reference (it includes CLI commands).

1) Install (dev)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

2) Configure

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
qwayk-callrail-safe-agent-cli onboarding
```

3) Smoke test

```bash
qwayk-callrail-safe-agent-cli auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
qwayk-callrail-safe-agent-cli --output json --version
```

4) Run one safe read:

```bash
qwayk-callrail-safe-agent-cli --output json accounts list
```

5) Dry-run a write before applying

```bash
qwayk-callrail-safe-agent-cli --output json --env-file .env \
  tags create --account-id acc_example --payload-json '{"name":"VIP Lead","color":"blue"}'
```

6) Apply with explicit safety flags

```bash
qwayk-callrail-safe-agent-cli --output json --env-file .env \
  tags create --account-id acc_example --payload-json '{"name":"VIP Lead","color":"blue"}' --apply --yes --ack-no-snapshot
```

Use `--ack-irreversible` only for `calls create-outbound` and `text-messages send`.

By default the tool keeps run artifacts. If disabled, receipts and plans are not written.
