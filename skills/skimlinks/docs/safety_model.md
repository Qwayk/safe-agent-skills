# How this skill stays safe

This skill ships read commands, read-like Product Key POST lookups, and a local Link Wrapper URL builder.

There are no live Skimlinks mutation commands in this release.

## Safety rules

- No raw request bridge.
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
