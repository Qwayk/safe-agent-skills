# Safety model

Skimlinks is safest when you treat the agent as a focused reader for merchant search, reporting, Product Key lookups, and local link wrapping. It can help with research and reporting, but it should not be used as proof until it has fetched the actual records behind the summary.

The main safety job is simple: stay inside the supported read surface, keep any saved output private when it contains business data, and avoid broad conclusions from thin list results.

A good safety ask is: "Read the merchant or report first, then keep link-wrapper output local and treat Product Key results as read-like lookups."

## Core safety rules

This skill ships read commands, read-like Product Key POST lookups, and a local Link Wrapper URL builder.

There are no live Skimlinks mutation commands in this release.

## Safety rules

- No unreviewed direct API passthrough.
- No hidden endpoints.
- No credentials or access tokens in stdout, stderr, logs, examples, or docs.
- Product Key access is not flattened into the shared auth model.
- Link Wrapper does not click links or follow redirects.
- Data Pipe and Skimlinks JavaScript are documented as official non-API areas, not counted as shipped CLI command families.

## What this means in practice

- Merchant, Reporting, and Product Key work only read or query official Skimlinks surfaces.
- The main setup risk is wrong credentials, the wrong publisher ID, or the wrong publisher domain ID.
- Product Key can fail even when standard Merchant and Reporting auth works, because Skimlinks may gate Product Key separately.
- `onboarding` can create a local placeholder `.env`, but it never writes secrets for you.

If write commands are ever added later, they must use the repo-standard plan, review, apply, verify, and receipt flow.
