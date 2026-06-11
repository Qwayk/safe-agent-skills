# Proof

Purpose:
- Show why the live coverage claim is trustworthy.
- Keep the proof small, concrete, and reproducible.

## Coverage proof

- Live official audit date (UTC): `2026-04-27`
- Official source only: Cloudflare API sitemap plus official method pages
- Active allowlisted operations after the refresh: `2350`
- The refresh reconciled the official Cloudflare method inventory with the local allowlist.

## Safety proof

- The runtime allowlist is now loaded from `docs/_generated/live_official_api_inventory.json`.
- The CLI still exposes only explicit allowlisted commands: `cloudflare-api-tool operations <area> <op_key>`.
- Dangerous allowlisted writes now save the live old-state in `before_state` and `before_state_path` before apply, or require explicit no-snapshot approval for live apply when no safe before-state path exists.
- Named remote-write helpers need either saved before-state support or explicit no-snapshot approval with a clear receipt before apply; named read-like/file-output helpers still apply safely.
- The new `browser-run` front door delegates to the same allowlisted Browser Rendering operations instead of adding a raw request path.
- Sensitive reads and sensitive write results stay file-only.
- New live AI Search search and chat endpoints are treated as read-like POSTs.
- Browser Rendering and Workers Tail start are treated as read-like POSTs.
- New live browser-rendering, custom-pages, vuln-scanner, brand-protection, warp-connector, and email-sending surfaces stay under conservative file-only handling.
- Targeted live smoke on `2026-04-30` succeeded for `browser-run markdown`, `links`, `scrape`, `screenshot`, `crawl`, and `crawl-result` against `https://example.com/`.

## Checks

- `.venv/bin/python -m unittest -q`
- Last full unit result (UTC `2026-06-04`): `Ran 317 tests in 11.616s` and `OK`

## Artifacts

- `docs/_generated/live_official_api_inventory.json`
- `docs/api_coverage_live_official.md`
- `docs/api_coverage.md`
- `docs/references.md`
