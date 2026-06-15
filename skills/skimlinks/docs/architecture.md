# Architecture

Skimlinks is built as a small command-line tool for merchant search, reporting, Product Key lookups, and local link wrapping. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Skimlinks.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Skimlinks."

## Architecture notes

Main layers:
- `cli.py`: parser and shared output/error flow.
- `config.py`: `.env` parsing and non-secret environment fingerprint.
- `skimlinks.py`: temporary-token auth and Skimlinks request helpers.
- `http.py`: `requests` wrapper with token-style URL redaction.
- `commands/merchant.py`: Merchant API commands.
- `commands/reporting.py`: Reporting API commands.
- `commands/product_key.py`: Product Key commands.
- `commands/link_wrapper.py`: local Link Wrapper URL builder.
- `commands/onboarding.py`: first setup helper.
- `audit_log.py`: optional JSONL audit logs with redaction.
- `runs.py`: local run history helpers.

The CLI is read-only or read-like in v0.1.0. Product Key batch lookup uses POST because the official API does, but it does not mutate Skimlinks data.
