# Architecture

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
