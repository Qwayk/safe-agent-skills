# Quickstart

Use Python 3.12 or newer. From the installed skill folder, run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/skimlinks-safe-cli --version
```

To check merchants or pull a report, run onboarding and fill in the fields from Publisher Hub before running the sign-in check. See [Connect your Skimlinks account](onboarding.md) if you use a separate settings file.

```bash
.venv/bin/skimlinks-safe-cli onboarding
.venv/bin/skimlinks-safe-cli auth check
```

Start with a small search. If the result shows `has_more: true`, Skimlinks has another page. Pass `--offset 10` to continue this example with the same filters.

```bash
.venv/bin/skimlinks-safe-cli merchant merchants list --search laptop --country US --limit 10
```

For a link report, choose a date range and what you want to group and count. This example groups clicks by merchant.

```bash
.venv/bin/skimlinks-safe-cli reporting link-report query --start-date 2026-01-01 --end-date 2026-01-31 --dim merchant_id --met clicks
```

If you only need an affiliate link, use your Site ID and the full destination URL. This example builds the URL without opening it.

```bash
.venv/bin/skimlinks-safe-cli link-wrapper build --id 123X456 --url 'https://merchant.example/product?sku=abc'
```

See [the command guide](command_reference.md) for more options.
