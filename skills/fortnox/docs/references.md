# References (sources)

This page lists the public Fortnox docs used to map the skill. Use it when you want to check where an auth rule, endpoint family, rate limit, websocket topic, or coverage decision came from.

Only official Fortnox sources are used here. Do not add secrets, tokens, callback URLs with codes, private tenant data, or copied live responses to this file.

## Provider docs (official)

- Provider: `Fortnox`
- API docs home: `https://api.fortnox.se/apidocs`
- Developer home: `https://www.fortnox.se/developer`
- Developer Portal: `https://www.fortnox.se/developer/developer-portal`
- Auth overview: `https://www.fortnox.se/developer/authorization`
- Auth code: `https://www.fortnox.se/developer/authorization/get-authorization-code`
- Access token: `https://www.fortnox.se/developer/authorization/get-access-token`
- Refresh token: `https://www.fortnox.se/developer/authorization/get-refresh-token`
- Client credentials: `https://www.fortnox.se/developer/authorization/get-access-token-using-client-credentials`
- Request auth/header guidance: `https://www.fortnox.se/developer/authorization/make-request`
- Token revoke: `https://www.fortnox.se/developer/authorization/revoke-access-token`
- Guides index: `https://www.fortnox.se/developer/guides-and-good-to-know`
- Header fields: `https://www.fortnox.se/developer/guides-and-good-to-know/header-fields`
- Scopes: `https://www.fortnox.se/developer/guides-and-good-to-know/scopes`
- Rate limits: `https://www.fortnox.se/developer/guides-and-good-to-know/rate-limits-for-fortnox-api`
- Errors: `https://www.fortnox.se/developer/guides-and-good-to-know/errors`
- Websockets: `https://www.fortnox.se/developer/guides-and-good-to-know/websockets`
- Endpoint consolidation note: `https://www.fortnox.se/developer/blog/fortnox-api-endpoint-consolidation`
- Last verified (UTC): `2026-06-09`

## Official source notes

- `https://api.fortnox.se/apidocs` is the canonical REST docs front door and the current coverage lock is derived from that rendered official page.
- The same page publishes an OpenAPI download link, but direct download returned HTTP `429` from this environment on `2026-06-09`, so the current vendored REST inventory is taken from the rendered docs page itself.
- The websocket docs page publishes the stream URL `wss://ws.fortnox.se/topics-v1`, the official control commands, and the topic/event matrix used in the vendored websocket inventory.

## Other sources

- None. This tool currently uses official Fortnox docs only.
