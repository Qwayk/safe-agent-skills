# Troubleshooting

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
