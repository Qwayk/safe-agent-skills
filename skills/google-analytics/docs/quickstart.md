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
ga4-api-tool onboarding
```

3) Smoke test

```bash
ga4-api-tool auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
ga4-api-tool --output json --version
```

If you want to run the template without creating a real `.env` yet, you can point at `.env.example`:

```bash
ga4-api-tool --env-file .env.example auth check
```

4) Discovery method commands (reads execute; writes are dry-run by default)

All GA4 discovery methods are available as explicit commands:

- `ga4-api-tool admin v1alpha ...`
- `ga4-api-tool data v1beta ...`
- `ga4-api-tool data v1alpha ...`

The full list is committed in `docs/official_commands.txt`.

Example (read; executes the API call):

```bash
ga4-api-tool --env-file .env data v1beta properties run-report --property properties/123
```

Example (write; dry-run plan, no network):

```bash
ga4-api-tool --env-file .env admin v1alpha accounts patch --name accounts/123 --body-json '{}'
```

To request apply for a write, add `--apply` (and follow the risk gates in `docs/risk_gates.md`):

```bash
ga4-api-tool --env-file .env --apply admin v1alpha accounts patch --name accounts/123 --body-json '{}'
```

When no useful before-state can be saved, write apply requires explicit no-snapshot approval before GA4 HTTP. Approved supported writes must create a receipt that records the recovery limit.
