# Quickstart

This page is for people who want the commands.

If you are not ready for commands, start with [What this skill can help you do](use_cases.md), [Set up your account step by step](onboarding.md), and [See how this skill keeps changes safe](safety_model.md).

## Install for local use

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## Add your settings

Copy `.env.example` to `.env` and fill your values.

## First safety checks

```bash
qwayk-jobber-safe-agent-cli --output json onboarding
qwayk-jobber-safe-agent-cli --output json auth check
qwayk-jobber-safe-agent-cli --output json schema summary
```

## First Jobber-style read

```bash
qwayk-jobber-safe-agent-cli --output json read clients --selection "nodes { id name } totalCount" --limit 10
```

## First safe write plan

```bash
qwayk-jobber-safe-agent-cli --output json write clientCreate --args-json '{"input": {"firstName": "Sample", "lastName": "Client"}}' --selection 'client { id name } userErrors { message path }'
```

## Apply flow (plan first, then apply)

```bash
qwayk-jobber-safe-agent-cli --output json --plan-out plan.json write clientCreate --args-json '{"input": {"firstName": "Sample", "lastName": "Client"}}' --selection 'client { id name } userErrors { message path }'
qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json write clientCreate --args-json '{"input": {"firstName": "Sample", "lastName": "Client"}}' --selection 'client { id name } userErrors { message path }'
```

## OAuth token refresh and checks

```bash
qwayk-jobber-safe-agent-cli --output json auth token status
qwayk-jobber-safe-agent-cli --output json --apply --yes auth token refresh --refresh-token <refresh_token>
```

## Commands for webhook and jobs

```bash
qwayk-jobber-safe-agent-cli --output json webhooks topics
qwayk-jobber-safe-agent-cli --output json webhooks verify-signature --body-file payload.json --header X-Jobber-Hmac-SHA256=<from-header>
qwayk-jobber-safe-agent-cli --output json --plan-out plan.json jobs run --file examples/jobs.csv
qwayk-jobber-safe-agent-cli --output json --apply --yes --plan-in plan.json jobs run --file examples/jobs_with_write.csv
```
