# Quickstart

If you're non-technical, start with [What you can do](use_cases.md) and [Connect your account](onboarding.md).

This page is a technical reference (it includes CLI commands).

1) Install (minimal)

```bash
python3 -m venv .venv
. .venv/bin/activate
.venv/bin/python -m pip install -e .
```

Optional (dev extras):

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` -> `.env` and fill your Dynadot values.

If you want guided local setup first, run:

```bash
dynadot-api-tool onboarding
```

3) Smoke test

```bash
dynadot-api-tool auth check
```

If you want a safe version check with no `.env`:

```bash
dynadot-api-tool --output json --version
```

4) Read a quick domain inventory

```bash
dynadot-api-tool --output json domains list --all --out domains.list.json
```

You can also inspect a smaller read:

```bash
dynadot-api-tool --output json domains info --domain example.com
```

5) Preview a domain push

```bash
dynadot-api-tool --output json --plan-out push.plan.json domains push \\
  --to-push-username "<RECEIVER_PUSH_USERNAME>" \\
  --domains-file "<FILE>"
```

If you review the plan and approve it, the live apply path also needs `--ack-no-snapshot` because Dynadot writes here do not have a saved before-state:

```bash
dynadot-api-tool --output json --apply --yes --ack-no-snapshot \\
  --plan-in push.plan.json --receipt-out push.receipt.json \\
  domains push --to-push-username "<RECEIVER_PUSH_USERNAME>" --domains-file "<FILE>"
```

6) Preview a guided transfer run

```bash
dynadot-api-tool --output json --plan-out transfer.plan.json \\
  --env-file "<SENDER_ENV>" \\
  transfer run \\
  --receiver-env-file "<RECEIVER_ENV>" \\
  --to-push-username "<RECEIVER_PUSH_USERNAME>" \\
  --desired-ns "ns1.example.net" \\
  --desired-ns "ns2.example.net"
```

This plans the full sequence: push, receiver accept, presence check, name server fix, and summary.

7) Preview a name server migration

Export current name servers:

```bash
dynadot-api-tool --output json domains name-servers export \\
  --domains-export-in domains.list.json \\
  --out name_servers.current.json
```

Build the diff:

```bash
dynadot-api-tool --output json domains name-servers diff \\
  --current-in name_servers.current.json \\
  --desired-ns "ns1.example.net" \\
  --desired-ns "ns2.example.net" \\
  --out name_servers.diff.json
```

Preview the bulk set:

```bash
dynadot-api-tool --output json --plan-out ns.plan.json domains name-servers set --diff-in name_servers.diff.json
```
