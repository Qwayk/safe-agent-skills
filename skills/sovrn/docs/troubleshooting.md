# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Sovrn auth split

- If Commerce report commands fail, check `SOVRN_COMMERCE_SECRET_KEY` first.
- If Link Check, Bid Check, or product recommendation commands fail, check `SOVRN_COMMERCE_SITE_API_KEY`.
- If Advertising commands fail, make sure both `SOVRN_ADVERTISING_API_KEY` and `SOVRN_ADVERTISING_PUBLISHER_ID` are set.
