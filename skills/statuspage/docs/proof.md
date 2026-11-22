# Statuspage test results

## November 22, 2026 local checks

I built a fresh source download from each local copy and checked that it included the skill, `.env.example`, the guides and the saved Atlassian reply. I built a wheel from each download, then installed it outside the checkout. Each copy passed 27 tests both before and after installation. The installed command showed its help and version.

The tests used simulated replies. They checked all four public reads, including a reported outage, empty incident and maintenance lists, and replies that left out required data. They also checked that the chosen page and timeout take effect even when saved settings are invalid. No network requests ran.

The type check passed. Ruff still reports three existing style issues in `audit_log.py` and `test_imports.py`.

## Earlier evidence

The earlier verification record was dated June 11, 2026 (UTC) and named `https://status.atlassian.com` as the public page to check. The [saved examples](examples/README.md) show the replies and CLI output.

To check that public page live, run:

```bash
statuspage-api-tool --output json --base-url https://status.atlassian.com status get
```
