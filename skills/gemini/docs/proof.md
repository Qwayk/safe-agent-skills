# Proof And Verification

## June 29, 2026 build checks

## Checked

- The official `v1beta` and `v1` discovery documents were fetched from Google.
- Both discovery documents reported revision `20260626`.
- `docs/official_inventory.json` records 79 `v1beta` operations, 32 `v1` operations, and 82 merged explicit commands.
- The local test suite passed with 30 tests.
- Editable install smoke passed in a local `.venv`.
- Installed CLI smoke passed for `--version`, `auth check`, and a dry-run `cached-contents delete` plan.
- The apply-shaped `--ack-irreversible` path is covered by unit tests only: the matching-plan apply test mocks the Gemini HTTP response, and the mismatched-plan apply test proves the CLI refuses before any network call.
- The tests cover imports, CLI version, JSON parse errors, run artifacts, local OAuth-token storage, onboarding, jobs/demo safety behavior, Gemini registry counts, named command exposure, secret redaction, dry-run write plans, apply refusals, receipt writing, official upload paths, raw media upload, `multipart/related` metadata-plus-media upload bodies, documented acknowledgement placement, no-network apply refusal, and public example output portability.
- The review blockers are fixed: media uploads now use official `/upload/...` paths with `uploadType=media` for raw uploads and `uploadType=multipart` plus a `multipart/related` body when request metadata is supplied; `--ack-irreversible` works after state-changing subcommands as documented; and public example outputs no longer contain local machine paths.

## Commands Run

```bash
python3 -m unittest -q
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
.venv/bin/gemini-api-tool --output json --version
.venv/bin/gemini-api-tool --output json --env-file examples/example.env auth check
.venv/bin/gemini-api-tool --output json --env-file examples/example.env --plan-out /tmp/gemini-plan.json cached-contents delete --name cachedContents/example --ack-no-snapshot
git diff --check -- api-tools/qwayk-gemini-safe-agent-cli projects/qwayk-skills-control-room/workspaces/active/qwayk-gemini-safe-agent-cli
```

Result:

```text
Ran 30 tests in 0.227s

OK
```

## Not Live-Tested

No live Gemini account request was sent in this builder run because no real `GEMINI_API_KEY` was available in the workspace. Tests that need apply-shaped success mock the provider response. Tests that use the real CLI path for refusal assert that the HTTP sender is not called. Live behavior is therefore source-ready but live-unverified.

## Redaction

Tests verify that the API key header is redacted from planned requests and receipts.

## November 23, 2026 local checks

The source and local public copy each passed 36 offline tests. Both built a wheel and source archive. I installed each wheel in a fresh environment, checked all 82 named commands, and used the CLI from outside the checkout.

The installed checks created a private settings file at the chosen path, listed models with a simulated Gemini reply, blocked generation without spending approval, and sent a reviewed delete only once. The tests also covered changed upload bytes or keys, older plans, two applies at the same time, and a lost reply that left a receipt asking the agent to check the result.

Both skill files passed validation. I checked the links and the 60 files prepared for GitHub. The tests used fake keys and Gemini replies. No authenticated Gemini request was sent.
