# Quickstart

Technical reference: this page uses CLI commands. If you want the non-technical path, start with [use_cases.md](use_cases.md) and [onboarding.md](onboarding.md).

## Install and validate

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

## First local setup

```bash
cp .env.example .env
awin-advertiser-safe-cli --output json onboarding
awin-advertiser-safe-cli --output json auth check
```

## Common read examples

```bash
awin-advertiser-safe-cli --output json publishers list --advertiser-id 123456
awin-advertiser-safe-cli --output json reports publisher --advertiser-id 123456 --start-date 2026-06-01 --end-date 2026-06-30
awin-advertiser-safe-cli --output json transactions by-ids --advertiser-id 123456 --ids 1001,1002
```

## Common dry-run write examples

```bash
awin-advertiser-safe-cli --output json transactions batch validate --advertiser-id 123456 --batch-file /path/to/batch.json --plan-out plan.json
awin-advertiser-safe-cli --output json offers create --advertiser-id 123456 --offer-file /path/to/offer.json --plan-out offer-plan.json
awin-advertiser-safe-cli --output json product-feeds upload --advertiser-id 123456 --vertical retail --locale en_GB --feed-file /path/to/feed.jsonl --plan-out feed-plan.json
```

## Next technical references

- [command_reference.md](command_reference.md)
- [api_coverage.md](api_coverage.md)
- [proof.md](proof.md)
