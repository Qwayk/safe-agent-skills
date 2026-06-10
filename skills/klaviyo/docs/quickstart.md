# Quickstart

## 1) Install (dev)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2) Configure

```bash
cp .env.example .env
```

Fill values in `.env`:

- `KLAVIYO_API_BASE_URL` (usually `https://a.klaviyo.com`)
- `KLAVIYO_API_KEY`
- `KLAVIYO_COMPANY_ID` only for `/client/*` calls

## 3) Smoke test

```bash
klaviyo-safe-agent-cli auth check
```

## 4) Find supported operations

```bash
klaviyo-safe-agent-cli api ops list
```

Show one operation:

```bash
klaviyo-safe-agent-cli api ops show --op get_accounts
```

Run a read-only operation:

```bash
klaviyo-safe-agent-cli api get_accounts
```

Run a write operation in plan mode:

```bash
klaviyo-safe-agent-cli api create_coupon --body-json '{"data":{}}'
```

Test the write gate with an explicit plan:

```bash
klaviyo-safe-agent-cli --live --apply --yes --ack-no-snapshot --plan-in plan.json api create_coupon
```

With the reviewed plan and `--ack-no-snapshot`, that command can continue to live Klaviyo HTTP even though the tool did not save a snapshot first.
