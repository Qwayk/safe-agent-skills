# Configuration

Klaviyo configuration is the local setup an agent needs before it can review profiles, lists, segments, campaigns, flows, and email performance. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Klaviyo values are required, which ones are optional, and confirm the setup without showing secrets."

## Setup note

Read environment settings from `.env`, or from another file with `--env-file`.

## Files

- `.env.example`: copy this file to `.env` and fill values.
- `.state/runs`: local run history, plan files, refusal summaries, and future receipt files.

## Environment variables

Required:

- `KLAVIYO_API_BASE_URL`
  - Example: `https://a.klaviyo.com`

- `KLAVIYO_API_KEY`
  - Klaviyo private API key used for live calls.

Optional:

- `KLAVIYO_COMPANY_ID`
  - Required only for `/client/*` operations.

- `KLAVIYO_API_REVISION`
  - Default: `2026-04-15`

- `KLAVIYO_TIMEOUT_S`
  - Default: `30`
