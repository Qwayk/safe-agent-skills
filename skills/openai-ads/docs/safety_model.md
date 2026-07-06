# Safety Model

OpenAI Ads changes can affect spend, delivery, creative review, audience processing, account state, and conversion optimization. This CLI keeps the agent on a read-first, plan-first path.

## Reads

Read commands may run directly. They still redact API keys, auth headers, pixel IDs where private, raw audience rows, customer identifiers, emails, external IDs, and secret-looking URL parameters.

## Writes

Write commands do not apply by default. They create a plan with:

- operation and command
- target path and query values
- redacted request body
- risk reasons
- before-state status
- verification notes
- rollback limits

Live apply requires:

```bash
openai-ads-safe-agent-cli --apply --yes --plan-in plan.json ...
```

High-risk changes also require `--ack-irreversible`. No-snapshot changes also require `--ack-no-snapshot`. The CLI checks both the operation name and the request body, so a campaign body with a budget, active serving status, or targeting still gets the high-risk gate.

## High-risk families

- Activating, pausing, or archiving ad accounts, campaigns, ad groups, or ads.
- Budget, bid, targeting, and serving changes.
- Custom audience creation, upload, and archive.
- File upload.
- Conversion API keys, event settings, pixels, and server-side conversion events.
- Account brand and account serving state changes.

## Conversion events

Server-side conversion events default to validation behavior when planned. A real event send requires a reviewed plan and explicit approval because it can affect reporting and optimization. The CLI redacts event source URLs, identifiers, customer fields, and conversion API keys from normal output.

## No rollback promise

The CLI does not promise rollback for Ads changes. When it cannot save before-state, it says so in the plan and requires no-snapshot approval before apply.
