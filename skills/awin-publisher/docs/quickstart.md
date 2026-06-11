# Quickstart

Technical reference. If you want the simpler setup path, start with `use_cases.md` and `onboarding.md`.

1. Install in this folder

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Copy configuration

```bash
cp .env.example .env
```

3. Fill the keys you need in `.env`

- Always: `AWIN_API_TOKEN`
- Legacy feeds only: `AWIN_FEED_API_KEY`
- Proof of purchase only: `AWIN_PROOF_OF_PURCHASE_API_KEY` after Awin enables the publisher and the advertiser enables CLO

4. Run the setup check

```bash
awin-publisher-safe-cli onboarding
awin-publisher-safe-cli --output json auth check
```

5. Common reads

```bash
awin-publisher-safe-cli --output json accounts list
awin-publisher-safe-cli --output json programs list --publisher-id <publisher_id>
awin-publisher-safe-cli --output json offers list --publisher-id <publisher_id>
awin-publisher-safe-cli --output json transactions list --publisher-id <publisher_id> --start-date 2026-06-01T00:00:00Z --end-date 2026-06-02T00:00:00Z --timezone UTC
awin-publisher-safe-cli --output json reports advertiser --publisher-id <publisher_id> --start-date 2026-06-01 --end-date 2026-06-02 --region GB
```

6. File downloads

```bash
awin-publisher-safe-cli --output json feeds enhanced-download --publisher-id <publisher_id> --advertiser-id <advertiser_id> --locale en_GB --out enhanced-feed.jsonl
awin-publisher-safe-cli --output json feeds legacy-list --out legacy-feed-list.csv
```

7. Safe write flow for proof of purchase

```bash
awin-publisher-safe-cli --output json --plan-out proof-plan.json proof-of-purchase orders create --publisher-id <publisher_id> --advertiser-id <advertiser_id> --orders-file orders.json
awin-publisher-safe-cli --output json --apply --yes --plan-in proof-plan.json --receipt-out proof-receipt.json proof-of-purchase orders create --publisher-id <publisher_id> --advertiser-id <advertiser_id> --orders-file orders.json
```

Official gating still applies to the live proof-of-purchase command: Awin must enable the publisher and the advertiser must enable CLO for that program.

8. Validation

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```
