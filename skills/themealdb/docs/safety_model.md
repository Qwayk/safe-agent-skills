# Safety model

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
- No raw request bridge
- No generic “call anything” command

## Safety checks

- `auth check` confirms the API is reachable with a read-only probe
- `docs/api_coverage.md` is the main reference for the allowed endpoint list
- `docs/proof.md` and `docs/examples/outputs/` show real command evidence

## Output safety

- JSON mode prints exactly one object to stdout
- Audit logs are optional and stay local
- Custom API keys are never echoed back in normal output
