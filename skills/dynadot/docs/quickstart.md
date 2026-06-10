# Quickstart

If you’re non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is a technical reference (it includes CLI commands).

1) Install (dev)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
dynadot-api-tool onboarding
```

3) Smoke test

```bash
dynadot-api-tool auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
dynadot-api-tool --output json --version
```

If you want to run the template without creating a real `.env` yet, you can point at `.env.example`:

```bash
dynadot-api-tool --env-file .env.example auth check
```

4) Push domains (preview first, then approved apply or exact refusal)

Current write apply requires explicit no-snapshot approval before Dynadot HTTP when no saved snapshot is available.

Preview:

```bash
dynadot-api-tool --output json --plan-out plan.json domains push --to-push-username "<RECEIVER_PUSH_USERNAME>" --domains-file "<FILE>"
```

Apply attempt:

```bash
dynadot-api-tool --output json --apply --yes --plan-in plan.json domains push --to-push-username "<RECEIVER_PUSH_USERNAME>" --domains-file "<FILE>"
```

4b) Transfer run (guided end-to-end plan, recommended for 1,000+ domains)

The dry-run plans the full sequence in the right order:
push (sender) → accept (receiver) → confirm → fix name servers → summary.

Preview (plan):

```bash
dynadot-api-tool --output json --plan-out plan.json --env-file "<SENDER_ENV>" transfer run --receiver-env-file "<RECEIVER_ENV>" --to-push-username "<RECEIVER_PUSH_USERNAME>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net"
```

Apply attempt (requires `--apply --yes` and reviewed `--plan-in`; currently requires explicit no-snapshot approval before sender/receiver HTTP):

```bash
dynadot-api-tool --output json --apply --yes --plan-in plan.json --env-file "<SENDER_ENV>" transfer run --receiver-env-file "<RECEIVER_ENV>" --to-push-username "<RECEIVER_PUSH_USERNAME>" --desired-ns "ns1.example.net" --desired-ns "ns2.example.net"
```

Note:
- These operational notes matter again after before-state support is added: Dynadot may require the sender account to be unlocked, and some domains may need renewal even when they look active.

5) Audit + set name servers (preview first, then approved apply or exact refusal)

Export your domains list (used as input for the next step):

```bash
dynadot-api-tool --output json domains list --all --out domains.list.json
```

Export current name servers:

```bash
dynadot-api-tool --output json domains name-servers export --domains-export-in domains.list.json --out name_servers.current.json
```

Diff vs desired name servers:

```bash
dynadot-api-tool --output json domains name-servers diff --current-in name_servers.current.json --desired-ns "ns1.example.net" --desired-ns "ns2.example.net" --out name_servers.diff.json
```

Preview a bulk set (plan file):

```bash
dynadot-api-tool --output json --plan-out plan.json domains name-servers set --diff-in name_servers.diff.json
```

Apply attempt (requires `--apply --yes` and reviewed `--plan-in`; currently requires explicit no-snapshot approval before `set_ns`):

```bash
dynadot-api-tool --output json --apply --yes --plan-in plan.json domains name-servers set --diff-in name_servers.diff.json
```
