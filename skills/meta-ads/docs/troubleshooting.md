# Troubleshooting

## “Missing META_ADS_ACCESS_TOKEN”

- Run: `meta-ads-api-tool onboarding`
- Ensure your `.env` has a real token:
  - `META_ADS_ACCESS_TOKEN=...`

Never paste the token into chat.

## Graph API error: OAuthException / code=190

This usually means the token is invalid or expired.

- Regenerate a token in Meta’s UI/tooling.
- Replace `META_ADS_ACCESS_TOKEN` in `.env`.
- Re-run: `meta-ads-api-tool --output json auth check`

## Graph API error: permissions / access denied

Common causes:
- Token missing `ads_read`
- Token is for a different Business / does not have access to the ad account
- Using an ad account id you don’t have access to

Try:
- `meta-ads-api-tool --output json ad-accounts list --fields id,name`
- If that fails, fix the token permissions/access in Meta first.

## Snapshot export is “partial_success”

By default, `snapshot export` continues when a surface/chunk fails (common with large fieldsets or missing permissions) and records the gap in `manifest.json`.

Options:
- Keep partial-success and use the manifest to understand what’s missing.
- Re-run with a smaller preset (example: `ecom_core` instead of `maximal_firehose`).
- Use `--strict` to fail fast if *any* chunk/surface fetch fails.

## Previews output contains HTML

`previews get` returns HTML snippets in JSON.

Notes:
- Treat preview HTML as untrusted text.
- If you render it, render in a sandboxed environment.

## Asset downloads

Asset downloads are local-only and opt-in:

- Enable: `--download-assets`
- Overwrite control: `--assets-overwrite never|if_missing|always`

If downloads fail:
- Check that URLs are reachable from your machine/network.
- Re-run with `--verbose` for redacted request logging.

## Rate limits (HTTP 429)

The tool retries 429/5xx with backoff (up to `META_ADS_MAX_RETRIES`).
If you still hit 429 repeatedly:
- Reduce scope (smaller date ranges, fewer breakdowns).
- Lower `--max-pages` / `--max-items`.
- Try again later.

## Wrong API version

If you override `META_ADS_API_VERSION` and requests fail unexpectedly:
- Remove the override and use the default (`v24.0` in this repo snapshot).
