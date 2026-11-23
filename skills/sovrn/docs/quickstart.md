# Get your first Sovrn result

Use Python 3.12 or newer. Run these commands in the skill folder that contains `pyproject.toml`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/sovrn-safe-cli --version
.venv/bin/sovrn-safe-cli --env-file .env onboarding
```

Add the key you need to the new settings file. For Advertising, add the publisher ID too. Keep the file private.

```bash
.venv/bin/sovrn-safe-cli --env-file .env auth check
```

This check shows which settings you filled in. Pick one request below to see whether the key can read the data you want.

## Check a link with a Commerce site API key

Replace the example URL with the product page you want to check.

```bash
.venv/bin/sovrn-safe-cli --env-file .env commerce links check --url https://example.com/product
```

## Check page earnings with a Commerce secret key

Set the dates you want. The end date is the first day outside the report.

```bash
.venv/bin/sovrn-safe-cli --env-file .env commerce reports pages get --click-date-start 2026-01-01 --click-date-end 2026-01-02
```

## Check ad earnings with an Advertising key and publisher ID

This report groups one day's revenue by where the ad traffic came from. Use dates in UTC.

```bash
.venv/bin/sovrn-safe-cli --env-file .env advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction
```

Ask your agent which site or publisher it used, what the result showed, and what you should check next if a result is empty or incomplete.

[Find your key](onboarding.md) · [All commands](command_reference.md)
