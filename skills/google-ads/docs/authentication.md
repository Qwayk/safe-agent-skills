# Authentication

This tool uses the Google Ads API authentication model:

## Required values

- Google Ads developer token (from Google Ads UI)
- OAuth2 client id + client secret (from Google Cloud Console)
- OAuth2 refresh token for the Google Ads API scope

All values live in `.env` (gitignored). The tool does not store tokens under `.state/`.

## Recommended onboarding flow

1) Run `google-ads-api-tool onboarding` to create `.env` from `.env.example`.
2) Fill `.env` with your values (never paste them into chat).
3) Run `google-ads-api-tool --output json auth check`.

## References (official)

See `docs/references.md`.
