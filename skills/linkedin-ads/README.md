# linkedin-ads-api-tool

`linkedin-ads-api-tool` is a safety-first CLI for LinkedIn Ads API actions.

It runs LinkedIn Ads API actions with a safe default flow:

- Operations marked `read` run live, including read-like `POST` actions.
- Operations marked `write-apply` or `write-apply-yes` run as plans by default.
- Current write applies require explicit no-snapshot approval before LinkedIn HTTP until safe before-state capture exists.
- Keep proof files for write-capable runs.

LinkedIn access is often approval-gated. Many surfaces are restricted:
- Matched Audiences
- Audience Insights
- Media Planning
- Company Intelligence

Use this tool only after your LinkedIn app has the needed product approvals and scopes.

Default settings are:
- `base URL`: `https://api.linkedin.com/rest`
- `LinkedIn version`: `202605`
- `X-Restli-Protocol-Version`: `2.0.0`
- `timeout`: `30s`

## Start here if you are non-technical

- `docs/use_cases.md`
- `docs/onboarding.md`
- `docs/safety_model.md`
- Agent skill prompt and install notes are included with this package.

## Start here if you are technical

- `docs/quickstart.md`
- `docs/command_reference.md`
- `docs/configuration.md`
- `docs/authentication.md`

## Proof and coverage

- `docs/api_coverage.md` is the main reference for all LinkedIn families and operations this CLI exposes.

## Example checks

```bash
linkedin-ads-api-tool --output json --version
linkedin-ads-api-tool --output json auth check
```
