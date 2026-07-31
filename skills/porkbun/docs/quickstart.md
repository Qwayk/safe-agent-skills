# Quickstart

List the domains in your Porkbun account, then decide whether you only need a review or want to prepare a change.

## 1) Install locally (if you run source)

```bash
cd api-tools/qwayk-porkbun-safe-agent-cli
python3 -m venv .venv
. .venv/bin/activate
.venv/bin/python -m pip install -e '.[dev]'
```

## 2) Create the private env file and check the CLI

```bash
porkbun --version
porkbun --output json onboarding
```

`onboarding` creates `.env` atomically with owner-only `0600` permissions. Fill in `PORKBUN_API_KEY` and `PORKBUN_SECRET_API_KEY` there. Keep both values out of chat and shell arguments.

Then check authentication:

```bash
porkbun --output json auth check
```

`auth check` is read-only. If credentials are not set, it reports `authenticated: false` and makes no provider request.

## 3) See one real read result

After onboarding is complete:

```bash
porkbun --output json --env-file .env domain get-domains
```

The tool starts with safe reads, and write commands need explicit plan + approval before they can apply.

## 4) Find pricing and transfer checks

```bash
porkbun --output json pricing get-pricing-get
porkbun --output json pricing get-pricing --input pricing.json
```

The POST form reads its JSON body from `pricing.json`; `--input` never accepts inline JSON. Use the result to decide whether your next step is registration planning or only an account review.

## 5) Check an account invitation safely

Put the invitation token in an owner-only JSON file:

```json
{"token":"INVITE_TOKEN"}
```

```bash
chmod 600 invite-status.json
porkbun --output json --env-file .env account get-account-invite-status --input invite-status.json
```

The token is accepted only from the JSON `--input` file. Never pass it with `--token`; that form is rejected so the token does not appear in the process command line.

## Before your first write

A write command first saves a plan. The CLI authenticates that plan with HMAC-SHA256 using `.state/plan-signing.key`. Run plan and apply from the same working directory with the same local `.state`; copying only the plan to another machine or directory is not enough.

The CLI writes plans and receipts atomically as `0600` files. Tool-created `.state` directories use `0700`, and the signing key uses `0600`. Secret-bearing commands also require `--ack-secret` and `--secret-out`. The destination is checked and reserved before any provider call, so an unsafe or unwritable destination stops the command without contacting Porkbun.

Redirects are disabled, and every `3xx` response is treated as a failure.

This tool keeps Porkbun’s 53-path boundary as 66 fixed commands: 39 reads and 27 writes. It can call only `https://api.porkbun.com/api/json/v3` or `https://api-ipv4.porkbun.com/api/json/v3`. Repository verification used no live Porkbun account and made no live provider calls.

If you want commands for everything, open the [full command guide](command_reference.md).
