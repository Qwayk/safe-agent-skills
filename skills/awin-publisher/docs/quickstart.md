# Quickstart

If you want the plain-English path first, start with [What you can do with Awin Publisher](use_cases.md), [Connect your Awin publisher account](onboarding.md), and [How this skill stays safe](safety_model.md).

## Install and validate

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## First local setup

```bash
cp .env.example .env
awin-publisher-safe-cli onboarding
awin-publisher-safe-cli --output json auth check
```

Fill the keys you need in `.env`:

- Always: `AWIN_API_TOKEN`
- Legacy feeds only: `AWIN_FEED_API_KEY`
- Proof of purchase only: `AWIN_PROOF_OF_PURCHASE_API_KEY` after Awin enables the publisher and the advertiser enables CLO

## Common read examples

```bash
awin-publisher-safe-cli --output json accounts list
awin-publisher-safe-cli --output json programs list --publisher-id <publisher_id>
awin-publisher-safe-cli --output json offers list --publisher-id <publisher_id>
awin-publisher-safe-cli --output json transactions list --publisher-id <publisher_id> --start-date 2026-06-01T00:00:00Z --end-date 2026-06-02T00:00:00Z --timezone UTC
awin-publisher-safe-cli --output json reports advertiser --publisher-id <publisher_id> --start-date 2026-06-01 --end-date 2026-06-02 --region GB
```

## Download examples

```bash
awin-publisher-safe-cli --output json feeds enhanced-download --publisher-id <publisher_id> --advertiser-id <advertiser_id> --locale en_GB --out enhanced-feed.jsonl
awin-publisher-safe-cli --output json feeds legacy-list --out legacy-feed-list.csv
```

## Safe proof-of-purchase flow

```bash
awin-publisher-safe-cli --output json --plan-out proof-plan.json proof-of-purchase orders create --publisher-id <publisher_id> --advertiser-id <advertiser_id> --orders-file orders.json
awin-publisher-safe-cli --output json --apply --yes --plan-in proof-plan.json --receipt-out proof-receipt.json proof-of-purchase orders create --publisher-id <publisher_id> --advertiser-id <advertiser_id> --orders-file orders.json
```

Official gating still applies to the live proof-of-purchase command: Awin must enable the publisher and the advertiser must enable CLO for that program.

## Validation

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

## Next references

- [Command reference](command_reference.md)
- [Authentication details](authentication.md)
- [Configuration](configuration.md)
- [Proof and verification](proof.md)
- [API coverage](api_coverage.md)
