# Authentication

Google Ads authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For customer access, GAQL reads, campaign settings, budgets, criteria, and bulk mutate work, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Google Ads credential path is configured, run the safe auth check, and stop before any token write or live account change."

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
