# Authentication

Sovrn authentication is the part that decides which account the agent can see and which actions it can even plan. Keep the credential setup local, use the safe check first, and do not paste secrets or token files into chat.

For publisher commerce, advertising reports, merchants, links, and performance data, the exact credential path is listed below. When OAuth is required, it means the user approves access through the provider instead of copying a long-lived password into the tool.

A good first auth check is: "Check which Sovrn credential path is configured, run the safe auth check, and stop before any token write or live account change."

## Authentication notes

This tool does not use OAuth. It uses the official Sovrn credential shapes directly.

## Commerce secret header

- Header format: `Authorization: secret {SECRET_KEY}`
- Used by Commerce campaigns, real-time reports, merchant-rate endpoints, and some mixed product flows

## Commerce site API key

- Used where the official docs require `key`, `apiKey`, `api_key`, or `{site-api-key}`
- Used by Link Check, Bid Check, Product Recommendation, and part of mixed product flows

## Mixed Commerce auth

- Product Promo Codes requires both:
  - `SOVRN_COMMERCE_SECRET_KEY`
  - `SOVRN_COMMERCE_SITE_API_KEY`
- Price Comparisons also requires both:
  - `SOVRN_COMMERCE_SECRET_KEY`
  - `SOVRN_COMMERCE_SITE_API_KEY`

## Advertising reporting

- Header: `x-api-key: {API_KEY}`
- Path requirement: `publisherId`
- Used by all shipped Advertising reporting commands

## Current auth check note

`sovrn-safe-cli auth check` is a local config check only.
It does not call the network.

It reports:
- which env values are present
- which real command bundles are ready
- whether the full tool has every auth value needed for the whole shipped surface

Use the real `commerce` and `advertising` read commands for live vendor proof.
