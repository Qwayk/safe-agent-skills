# Troubleshooting

## Common issues for this tool

### 1) Missing token

You will see `Missing LinkedIn token...` from validation.

- If needed, add one of:
  - `LINKEDIN_ADS_ACCESS_TOKEN`
  - `LINKEDIN_ADS_TOKEN`
  - `LINKEDIN_ADS_API_TOKEN`
- Or run:
  - `linkedin-ads-api-tool auth token set --file token.json`
- Check status:
  - `linkedin-ads-api-tool auth token status`

### 2) Missing approvals / private gates

LinkedIn can return `403` for approved-gate endpoints.

- Run `linkedin-ads-api-tool --output json auth check` first.
- If this succeeds but operations fail, the app still needs product or scope access.
- Check `docs/api_coverage.md` for `access-gated`, `private-api-gated`, and `tier-gated` labels.

### 3) Expired token

- If a token is expired, refresh it using your OAuth flow.
- Replace token file with:
  - `linkedin-ads-api-tool auth token set --file token.json`
- Re-run `auth check`.

### 4) Wrong LinkedIn version / protocol headers

- Confirm `.env` has:
  - `LINKEDIN_ADS_LINKEDIN_VERSION=202605`
  - `LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION=2.0.0`
- Use a clean `.env` from `.env.example` and rerun onboarding if needed.

## Debug tips

- Use `--verbose` for one request line and timing output.
- Use `--debug` only for local developer investigation of full stack traces.
- By default the tool emits one JSON object for errors and never prints token values.
