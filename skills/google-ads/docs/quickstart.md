# Quickstart

If you’re non-technical, start with:
- `use_cases.md`
- `onboarding.md`

This page is a technical reference (it includes CLI commands).

1) Install (dev)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

2) Configure

Copy `.env.example` → `.env` and fill your values.

Tip: for a guided first-time setup, run:

```bash
google-ads-api-tool onboarding
```

3) Smoke test

```bash
google-ads-api-tool auth check
```

If you want a safe machine-readable version output (no `.env` required):

```bash
google-ads-api-tool --output json --version
```

4) Run a GAQL query (read)

```bash
google-ads-api-tool gaql --customer-id YOUR_CUSTOMER_ID --query "SELECT customer.id FROM customer LIMIT 1" --limit 1
```

5) List presets (no GAQL knowledge required)

```bash
google-ads-api-tool presets list
google-ads-api-tool presets show --preset optimization_pack_v1
google-ads-api-tool presets show --preset analysis_pack_v2
google-ads-api-tool presets show --preset analysis_pack_max_v1
google-ads-api-tool presets validate
```

6) Export a snapshot optimization pack (dry-run → apply)

Dry-run (no API calls, no out-dir written):

```bash
google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack
```

Apply (read-only to Google Ads; writes local pack files):

```bash
google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --apply --yes
```

Include optional preset groups (recommended for deeper analysis; may increase time/quota):

```bash
google-ads-api-tool snapshot export --preset optimization_pack_v1 --customer-id YOUR_CUSTOMER_ID --since 2026-01-01 --until 2026-01-31 --out-dir ./out/google-ads-pack --apply --yes --include-optional
```

7) Use explicit RPC methods (advanced)

Command shape:

```bash
google-ads-api-tool <service-kebab> <method-kebab> --in request.json
```

Write RPCs are plan-first by default:

```bash
google-ads-api-tool campaign-service mutate-campaigns --in mutate_campaigns_request.json
```

7b) Offline optimization diagnosis from a pack (no API calls)

```bash
google-ads-api-tool snapshot analyze diagnose --pack-dir ./out/google-ads-pack
```

Legacy best-effort optimization report:

```bash
google-ads-api-tool snapshot analyze optimize --pack-dir ./out/google-ads-pack
```
