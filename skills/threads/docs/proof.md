# Proof pack

Purpose:
- Say exactly what is proved locally.
- Separate local proof from live Threads verification that needs real app access and approved permissions.

## Last verified

- Date (UTC): 2026-06-04
- Tool version: `0.1.0`
- Provider API version: `v1.0`
- Environment: local sandbox

## Locally proved in this workspace

1. Unit and parser coverage

```bash
python3 -m unittest -q
.venv/bin/python -m unittest -q
```

Latest local result on 2026-06-04 UTC:
- `.venv/bin/python -m unittest -q` ran `66 tests` and returned `OK`

2. Binary and JSON contract

```bash
PYTHONPATH=src python3 -m threads_api_tool --output json --version
PYTHONPATH=src python3 -m threads_api_tool --output json auth check
```

Local proof from 2026-05-26 UTC:
- `--version` returns one JSON object with `tool`, `version`, and run metadata.
- `auth check` fails safely without a token and returns one JSON error object.

3. Dry-run write planning

```bash
PYTHONPATH=src python3 -m threads_api_tool --output json --plan-out /tmp/threads.plan.json posts create-text --threads-user-id demo-user --text Draft
```

Local proof from 2026-05-26 UTC:
- Write commands stay dry-run by default.
- The generated plan includes the official `media_type` and payload shape.
- Current write plans include blocked `before_state`.
- Current apply attempts require explicit no-snapshot approval before Threads provider writes, local token writes, demo/job writes, or receipt output.

4. Final reread and alignment

Local proof from 2026-05-26 UTC:
- The final reread closed CLI/docs drift for global flags and auth write behavior.
- Public read handlers across auth, profiles, posts, replies, mentions, insights, search, locations, and oEmbed now have direct command-level smoke coverage.

## Not proved live here

- No live Threads user token, app review state, or linked production account was available in this slice.
- All network-backed Threads endpoints remain `live-unverified` in `docs/api_coverage.md`.
- Provider-gated features such as profile discovery, keyword search, mentions, insights, and location tagging may still require Meta approval even though the CLI surface is implemented.

## Evidence files

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/auth_check.json`
- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json` (current refusal shape, not a successful write receipt)

The examples are synthetic/redacted shape references for the current plan-and-refuse behavior.
