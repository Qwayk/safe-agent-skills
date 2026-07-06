# Troubleshooting

## Missing API key

Run onboarding and fill `.env`:

```bash
openai-ads-safe-agent-cli onboarding
```

## Account check fails

Confirm the account has Ads Manager Beta access, API-key access, billing, and verification. Then run:

```bash
openai-ads-safe-agent-cli auth check
```

## Write refuses

Most refusals are safe no-ops. For live writes, create a plan first, review it, then apply with the same command plus `--apply --yes --plan-in`.

If the plan says no before-state snapshot is available, add `--ack-no-snapshot` only after reviewing that risk. If the plan affects spend, serving, uploads, audiences, account state, auth, or measurement, add `--ack-irreversible` only after reviewing that risk.
