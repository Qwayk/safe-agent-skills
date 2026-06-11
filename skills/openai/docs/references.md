# References (sources)

Purpose:
- Record what sources the tool implementation relies on (so behavior is auditable and reproducible).
- Prefer official provider docs; use other sources only when needed and note why.

Rules:
- Never include secrets (tokens, client secrets) in this file.
- When a capability depends on a specific documented behavior (rate limits, required headers, download tracking), link the exact doc page.
- Update this file whenever you add/change an endpoint or behavior based on new research.

## Provider docs (official)

- Provider: OpenAI
- API reference overview (navigation main reference for ops list): `https://developers.openai.com/api/reference/overview`
- OpenAPI spec (documented; referenced by OpenAI’s `openai/openai-openapi` README): `https://app.stainless.com/api/spec/documented/openai/openapi.documented.yml`
- Last audited (UTC): 2026-03-17
- Last verified (UTC): 2026-03-17

Pinned snapshots (committed in this tool repo):
- `docs/official_openapi_documented_v2.3.0_2026-03-17.yml` sha256: `52e344bdd29e39529ce2e45e481d7848a6a088a873f32ef438bed20be14aa4fa`
- `docs/official_operations_v1_2026-03-17.txt` sha256: `14e490cf0669bfc48c77530f14d6a4583d1fdfd4b024f29e15aadb54b672e622`
- Prior snapshot (still committed for audit history): `docs/official_openapi_documented_v2.3.0_2026-03-14.yml` sha256: `15ee0962f540a02a0bbc243e037ce76f47bfa00e332f91f9bb2b6299be5cc0ce`

## Other sources (only if needed)

None.
