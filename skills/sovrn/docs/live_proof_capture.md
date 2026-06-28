# Live proof capture

Use this page when real Sovrn credentials are available and you need to close the final customer-ready proof gap.

## Goal

Capture redacted successful outputs for the real shipped auth bundles:

- Commerce secret-header
- Commerce site-key
- Mixed Commerce auth
- Advertising `x-api-key` plus `publisherId`

Do not commit raw secrets, raw client account IDs, or private business data.

## Before you start

1. Add real values to `.env`.
2. Run `sovrn-safe-cli auth check` and confirm the needed command bundles are ready.
3. Review `docs/proof.md` and `docs/api_coverage.md` so the example set matches the shipped surface.

## Suggested proof commands

Commerce secret-header:

```bash
sovrn-safe-cli --output json commerce campaigns get --search PRIMARY > docs/examples/outputs/commerce_campaigns_success.json
```

Commerce site-key:

```bash
sovrn-safe-cli --output json commerce links check --url https://example.com/product > docs/examples/outputs/commerce_links_check_success.json
```

Mixed Commerce auth:

```bash
sovrn-safe-cli --output json commerce comparisons prices search --market usd_en --plainlink https://example.com/product > docs/examples/outputs/commerce_comparisons_success.json
```

Advertising:

```bash
sovrn-safe-cli --output json advertising reports account get --start 2026-01-01T00:00:00Z --end 2026-01-02T00:00:00Z --metrics publisherRevenue --dimensions auction > docs/examples/outputs/advertising_account_success.json
```

## Manual review before commit

Check each captured file for:

- no API keys
- no Authorization headers
- no publisher ID values that should stay private
- no user IP, consent, or tracking values
- no customer-only business data that should not be published

If needed, replace private values with obvious placeholders before commit.

If credentials are not available on the current machine:

- do not create fake success files
- keep the current local and negative examples under `docs/examples/outputs/`
- leave `docs/proof.md` honest about the missing live success proof

## After capture

1. Update `docs/proof.md` so the committed success examples are listed.
2. Update the `Last verified` block in `docs/proof.md`.
3. Remove or soften any wording that still says the tool is in active build.
4. Run the blessed validation command again.
5. Do the final strong review and only call the tool ready if the score reaches 100/100.
