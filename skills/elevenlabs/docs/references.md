# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: ElevenLabs (non-legacy API reference)
- API docs home: https://elevenlabs.io/docs/api-reference/introduction
- Auth docs (API key, `xi-api-key`, base URLs): https://elevenlabs.io/docs/api-reference/authentication
- Streaming guide + media outputs: https://elevenlabs.io/docs/api-reference/streaming
- Usage + rate limits hints: https://elevenlabs.io/docs/api-reference/usage/character-stats
- Last verified (UTC): 2026-03-29

Current doc notes validated in live testing:
- `GET /v1/usage/character-stats` requires `start_unix` and `end_unix` query params.
- Conversation search uses `text_query` rather than the older `query` wording still seen in some older examples.
- Test invocation listing requires `agent_id`.
- History download expects `history_item_ids`.

## Other sources (only if needed)

- None yet. Add extra references with a justification and verification date when you rely on non-official docs or vendor advisories.
