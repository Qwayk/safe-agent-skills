# Good first asks for Contentsquare

If you are not sure what to ask first, start with a read-only question. The agent can check what the account can access before it prepares any change.

## Good first asks

- “Check my Contentsquare OAuth access and tell me which endpoint URL it uses.”
- “List the export jobs for this project and tell me which ones ran successfully.”
- “Show the bounce rate, conversion rate, and visits for this project last week.”
- “List mappings, page groups, zonings, and zones so we know the right IDs before asking for metrics.”
- “Prepare a dry-run plan for a Data Export job for last week’s sessions.”
- “Prepare a dry-run plan to send this enrichment batch, and explain the risk before applying it.”
- “Get the last Speed Analysis monitoring report for this monitoring id.”
- “Prepare a reviewed plan before creating or deleting a Speed Analysis event.”

## What to expect back

For read-only work, expect a short answer plus the JSON result the CLI returned.

For live changes, expect a plan first. The plan should say what endpoint will be called, what body will be sent, why it has risk, and what proof will exist afterward.

## Best for

This CLI is best for server-side API work: exports, metrics, enrichment batches, and Speed Analysis Lab operations.

## Not best for

This CLI is not a Web Tag installer, WebView tracker, mobile SDK setup assistant, or Data Connect warehouse setup tool. Those docs are accounted for, but they are different product shapes.
