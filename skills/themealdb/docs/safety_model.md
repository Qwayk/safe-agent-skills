# Safety model

TheMealDB is safest when you treat the agent as a focused reader for public meals, ingredients, categories, areas, and recipe lookups. It can help with research and reporting, but it should not be used as proof until it has fetched the actual records behind the summary.

The main safety job is simple: stay inside the supported read surface, keep any saved output private when it contains business data, and avoid broad conclusions from thin list results.

A good safety ask is: "Run one meal, ingredient, or category lookup first, then summarize only from the returned recipe data."

## Core safety rules

This tool is safe by design because it is read-only.

## What the tool will do

- Read the documented free TheMealDB V1 public endpoints
- Use the public key `1` by default
- Return one JSON object in `--output json`
- Redact custom API keys from errors and verbose HTTP logs

## What the tool will not do

- No writes
- No uploads
- No premium V2 endpoints
- No unreviewed direct API passthrough
- No generic “call anything” command

## Safety checks

- `auth check` confirms the API is reachable with a read-only probe
- `docs/api_coverage.md` is the main reference for the allowed endpoint list
- `docs/proof.md` and `docs/examples/outputs/` show real command evidence

## Output safety

- JSON mode prints exactly one object to stdout
- Audit logs are optional and stay local
- Custom API keys are never echoed back in normal output
