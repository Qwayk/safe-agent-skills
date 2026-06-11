# Troubleshooting

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## Common setup problems

- **“Missing DYNADOT_API_KEY”** → put your API key in `.env` and re-run `dynadot-api-tool auth check`.
- **Wrong base URL** → for production use `https://api.dynadot.com/api3.json` (see `.env.example`).
- **Rate limit errors** → slow down / use smaller batches for read commands. Write apply currently requires explicit no-snapshot approval before Dynadot HTTP.
- **“Desired name servers are not available in this Dynadot account”** → add those name servers in the Dynadot UI first (or run without `--require-available-name-servers` if you only want a warning), then re-run.
- **“Please unlock your account firstly.”** → future transfer apply may need the sender Dynadot account unlocked in the control panel. Current write apply requires explicit no-snapshot approval before that provider call.
- **“Please renew your domain firstly: <domain>”** → that domain’s expiration date is in the past (it may still show `status=active` during grace). Renew it in Dynadot, then re-run (or use `--continue-on-error` to skip it today).
- **“Recipient account not set up to receive US domains…”** → the receiving account needs its “US app” + “US nexus” settings completed in the Dynadot control panel. After you save those settings, re-run (any `.us` domains will keep failing until this is set).
