# Quickstart

If you want the plain-English path first, start with [What you can do with Awin Advertiser](use_cases.md), [Connect your Awin advertiser account](onboarding.md), and [How this skill stays safe](safety_model.md).

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

`auth check` is the safest first live check because it uses the advertiser publishers endpoint to confirm the token and advertiser ID work together.

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

## Next references

- [Command reference](command_reference.md)
- [API coverage](api_coverage.md)
- [Proof and verification](proof.md)
