# Connect your Awin publisher account

You do not need to run every command yourself. This page exists so you or your AI agent can set the tool up safely.

## Before you start

- Always add `AWIN_API_TOKEN`.
- Add `AWIN_FEED_API_KEY` only if you need legacy feed list or legacy feed downloads.
- Add `AWIN_PROOF_OF_PURCHASE_API_KEY` only if you need proof-of-purchase order submission and that workflow is enabled for your publisher and advertiser program.

## Step-by-step setup

1. Copy `.env.example` to `.env`.
2. Fill the keys you actually need.
3. Run:

```bash
awin-publisher-safe-cli onboarding
awin-publisher-safe-cli --output json auth check
```

4. Confirm the output shows the publisher account you expect.
5. If you plan to use proof-of-purchase uploads, confirm first that Awin has enabled the publisher and the advertiser has enabled CLO for that program.

## What to ask your agent

- "Check whether my Awin token is working."
- "Show me which publisher accounts this token can access."
- "List joined programs for publisher 12345."
- "Download the enhanced feed for advertiser 6789 to a local file."
- "Prepare a dry-run proof-of-purchase upload from this JSON file."

## Important notes

- The tool never prints secrets back to the screen.
- `feeds enhanced-download`, `feeds legacy-list`, and `feeds legacy-download` only write local files when you give `--out`.
- `proof-of-purchase orders create` is the only remote write command. It starts in dry-run mode, and live apply requires `--apply --yes --plan-in`.
- Official proof-of-purchase live use needs both Awin Partner Development publisher enablement and advertiser CLO enablement in Tracking Settings -> Publisher Settings.
