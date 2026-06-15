# Safety model

Statuspage is safest when you treat the agent as a focused reader for public incidents, components, maintenances, subscribers, and status summaries. It can help with research and reporting, but it should not be used as proof until it has fetched the actual records behind the summary.

The main safety job is simple: stay inside the supported read surface, keep any saved output private when it contains business data, and avoid broad conclusions from thin list results.

A good safety ask is: "Read the page, incidents, and components first, then report the current status without trying to change the page."

## Core safety rules

It is built to check a public page and stay out of private account actions.

This skill is read-only:

- It only performs `GET` requests to public Statuspage API endpoints.
- It does not sign in or call private admin actions.
- It does not implement `--apply`, `--yes`, or plan/receipt flows because there are no writes here.
- The main safety question is whether you pointed the agent at the right public page, not whether a risky change might run.

## Output contract

- `--output json` prints exactly one JSON object to stdout.
- Errors are rendered as JSON with `ok=false` and an `error_type`.
