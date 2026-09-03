# Troubleshooting

Start by checking whether the failure is local validation, a missing safety approval, a provider response, or an account/plan limitation. Keep the single JSON error object; do not retry writes blindly.

## Local checks

Use `--debug` for a Python traceback and `--verbose` for request lifecycle lines on stderr. Secrets and API headers are redacted. JSON mode emits one JSON object.

## Authentication and permissions

Plan-only commands do not contact ElevenLabs. To test a key, run `auth check --live --out ./auth.json --overwrite`. For `401` or `403`, verify the key, workspace role, endpoint permissions, and selected base URL without printing the key.

## Safety refusals

Reads need `--live`. Writes need `--live --apply`; spend-sensitive operations also need `--ack-spend-money`. When no real before-state can be captured, apply additionally needs `--ack-no-snapshot`. Deletes, calls, and other irreversible operations may require `--yes` or `--ack-irreversible`. These refusals happen before provider HTTP.

## Provider limits and drift

Paid features, workspace allowlists, missing fixtures, rate limits, and endpoint-specific validation can block a correctly formed request. The local suite is offline, so live provider behavior is unverified for the current account. Check [API coverage](api_coverage.md), [proof](proof.md), and [references](references.md) before treating a failure as a CLI defect.
