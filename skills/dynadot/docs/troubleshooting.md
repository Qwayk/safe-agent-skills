# Troubleshooting

When Dynadot stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent inspecting domains, DNS records, nameservers, and account domain data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Dynadot error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

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
- **“Please renew your domain firstly: <domain>”** → that domain’s expiration date is in the past (it may still show `status=active` during grace). Renew it in Dynadot, then re-run (or use `--continue-on-error` to skip it for now).
- **“Recipient account not set up to receive US domains…”** → the receiving account needs its “US app” + “US nexus” settings completed in the Dynadot control panel. After you save those settings, re-run (any `.us` domains will keep failing until this is set).
