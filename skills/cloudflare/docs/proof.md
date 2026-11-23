# What has been verified

Use the dates below to see which checks used saved test data and which used Cloudflare.

## November 23, 2026 local checks

Fresh installs from the source and the local release folder each loaded all 2,350 operations from the included command list. The source passed 327 tests and the local release copy passed 330, with network access blocked. Both installs created a private settings file and used its path in the next command.

Simulated replies checked that a saved Worker deployment cannot apply a changed request. The check also caught a traffic split that differed from the request and kept a receipt when the deployment reply was unclear. The Pages tests caught changed files and an unexpected production branch before deployment. The DNS check caught a record that came back with different content.

The guide links were checked in both copies. The local release copy has five fewer guides. Its setup guide and command reference carry the steps people still need. This check used simulated Cloudflare replies.

## November 22, 2026 — Source cleanup

The source folder went from 6,075 tracked files to 227. The checkout tests for version 0.7.6 passed all 323 remaining tests with zero network attempts. The CLI loaded all 2,350 operations from the saved inventory. Twenty command examples parsed and `pip check` found no broken requirements. That check did not catch the missing inventory in the standalone package.

## November 22, 2026 — Standalone install and DNS guide

The CLI started from a fresh install in a folder outside the checkout. It loaded the same 2,350 operations and `pip check` passed. All 323 tests passed from both source and the installed package. The [quickstart](quickstart.md) reached the right account, zone, and DNS record using simulated Cloudflare replies. The guide now includes local skill setup, bringing the source folder to 226 files. The generator reproduces all seven certificate link fixes without fetching a new API inventory.

## Coverage proof

- Live official audit date (UTC): `2026-04-27`
- Official source only: Cloudflare API sitemap plus official method pages
- Active allowlisted operations after the refresh: `2350`
- The refresh reconciled the official Cloudflare method inventory with the local allowlist.

## Safety proof

- The CLI reads the [saved operation list](../src/cloudflare_api_tool/_data/live_official_api_inventory.json) from the installed package.
- The CLI still exposes only explicit allowlisted commands: `cloudflare-api-tool operations <area> <op_key>`.
- Dangerous allowlisted writes now save the live old-state in `before_state` and `before_state_path` before apply, or require explicit no-snapshot approval for live apply when no safe before-state path exists.
- Named remote-write helpers need either saved before-state support or explicit no-snapshot approval with a clear receipt before apply; named read-like/file-output helpers still apply safely.
- The new `browser-run` front door delegates to the same allowlisted Browser Rendering operations instead of adding a raw request path.
- Sensitive reads and sensitive write results stay file-only.
- An explicitly selected env file now fails closed when the path is invalid and supplies the Cloudflare values without process-environment override.
- `auth check`, `auth probe`, and `auth doctor` keep `cfat_` account tokens away from `/user/tokens/verify` and use account-scoped reads instead.
- `auth check` fails clearly when a user token is not active, no account is reachable, or the configured account does not match.
- New live AI Search search and chat endpoints are treated as read-like POSTs.
- Browser Rendering and Workers Tail start are treated as read-like POSTs.
- New live browser-rendering, custom-pages, vuln-scanner, brand-protection, warp-connector, and email-sending surfaces stay under conservative file-only handling.
- Targeted live smoke on `2026-04-30` succeeded for `browser-run markdown`, `links`, `scrape`, `screenshot`, `crawl`, and `crawl-result` against `https://example.com/`.

## Checks

- `.venv/bin/python -m unittest -q`
- Earlier full unit run (UTC `2026-11-09`): all 326 tests passed after the Email Routing docs were corrected to match the CLI.
- Full unit run (UTC `2026-06-04`): all 317 tests passed.
- Credential-change unit run (UTC `2026-08-23`): 325 of 326 tests passed. The Email Routing coverage ledger listed the wrong command name.
- Focused credential-selection result (UTC `2026-08-23`): account-token routing, user-token routing and status, account mismatch, explicit env-file precedence, invalid explicit paths, and account-token probe/doctor behavior passed.
- Account-token check (UTC `2026-08-02`): all 12 focused auth tests and the documentation checks passed.

## Artifacts

- [Saved operation inventory](../src/cloudflare_api_tool/_data/live_official_api_inventory.json)
- `docs/api_coverage_live_official.md`
- `docs/api_coverage.md`
- `docs/references.md`
