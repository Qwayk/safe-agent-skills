# Troubleshooting

When LinkedIn Ads stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing ad accounts, campaigns, creatives, targeting, and reporting, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the LinkedIn Ads error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

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
