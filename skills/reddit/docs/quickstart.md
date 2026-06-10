# Quickstart

This page is a technical reference with commands.
If you are non-technical, start with `docs/use_cases.md` and `docs/onboarding.md`.

## Local setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

## First commands

```bash
qwayk-reddit-safe-agent-cli --version
qwayk-reddit-safe-agent-cli onboarding
qwayk-reddit-safe-agent-cli auth login
qwayk-reddit-safe-agent-cli --live auth exchange-code --redirect-url '<paste redirect url>'
qwayk-reddit-safe-agent-cli api ops list --section account
```

## First live read

```bash
qwayk-reddit-safe-agent-cli --live auth exchange-code --redirect-url '<paste redirect url>'
qwayk-reddit-safe-agent-cli --live auth check
qwayk-reddit-safe-agent-cli --live api get-api-v1-me
```

## First write plan

```bash
qwayk-reddit-safe-agent-cli api post-api-vote --body id=t3_abc123 --body dir=1 --plan-out vote-plan.json
```

## Attempt the write after review

```bash
qwayk-reddit-safe-agent-cli --live --apply --plan-in vote-plan.json --yes api post-api-vote --body id=t3_abc123 --body dir=1
```

Approved writes should produce receipts that record explicit no-snapshot approval and recovery limits. If approval is missing, review the refusal and confirm no provider write happened.
