# Troubleshooting

When Plausible stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reading sites, traffic reports, goals, referrers, and analytics trends, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Plausible error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Debug HTTP

Use `--verbose` to see request start/end lines to stderr.

Secrets must never be printed (no Authorization headers, no tokens).

## Debug errors

By default the tool prints a single JSON error object.
If you want a full Python stack trace (developer debugging), add `--debug`.

## 401 Unauthorized

Make sure `PLAUSIBLE_API_KEY` is set in your `.env` and has access to the site.

## 400 “goal is not configured”

Some Plausible instances require a goal to be configured before you can query it via `event:goal`.

If you see errors like:
- `The goal \`members_confirmed\` is not configured for this site`

Create the goal in Plausible:
- Site → Goals → Add goal (event name must match exactly)

The membership funnel and reports will list these under `missing_goals` instead of failing.

## Self-hosted base URL

If you are self-hosting Plausible, ensure:
- `PLAUSIBLE_BASE_URL` is your instance root (example: `https://plausible-analytics.qwayk.com`)
- It responds to `GET /api/health` (the tool checks this in `auth check`)
