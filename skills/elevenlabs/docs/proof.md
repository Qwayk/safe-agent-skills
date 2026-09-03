# Proof and verification

This page separates deterministic repository proof from provider proof. Local tests use offline fixtures and mocks; they do not prove that a current ElevenLabs account can access or execute every operation.

## Pinned scope

- Snapshot: `openapi.json`
- SHA-256: `a82cfab5db1adc845ac5890bf536552a2f2c75836bdebff8019a80c1bf647cd1`
- HTTP boundary: 388 operations — 367 stable implemented, 21 deprecated
- Manual rows: seven WebSocket surfaces (six plan-only commands and one callback-only reverse connection), one callback-only Twilio webhook, and one docs-only authentication row
- Provider status: live behavior unverified for the current account

## Offline checks

From the tool folder:

```text
.venv/bin/python -m unittest -q
.venv/bin/elevenlabs-api-tool --output json --env-file .env.example auth check
.venv/bin/elevenlabs-api-tool --output json --env-file .env.example voices list
.venv/bin/elevenlabs-api-tool --output json --env-file .env.example models list
.venv/bin/elevenlabs-api-tool --output json --env-file .env.example tts synthesize --voice-id voice-123 --text hello --out ./out.mp3
```

The last command creates a plan only. It does not contact ElevenLabs or create audio.

To test a live account, use a real local env file, `--live`, and file output for sensitive/binary responses. No live result is claimed here.

## Write receipts

A write plan identifies the target, request, cost/external-action risk, verification, before-state status, and recovery limit. Apply requires a matching reviewed `--plan-in` and `--receipt-out`; where before-state capture is unavailable, it also requires `--ack-no-snapshot`. The receipt is seeded with durable pending-attempt evidence before provider I/O, then records what the CLI/provider returned. Output files receive local existence/size/SHA-256 evidence; eligible exact-path PUT/PATCH writes receive status-only GET readback (`readback_completed`/reachable), not value equality. Other writes remain explicitly unsupported.

The committed examples are deterministic fixtures:

- `docs/examples/plan.example.json`
- `docs/examples/receipt.example.json`

They contain placeholders and no credentials or private client data.

## Package proof (2026-09-03)

Built with the bundled environment using `python -m build --wheel --sdist`. The source
snapshot remains pinned at SHA-256 `a82cfab5db1adc845ac5890bf536552a2f2c75836bdebff8019a80c1bf647cd1`;
the generated runtime inventory is SHA-256
`53dee1fe15bd9045ba47e633e782ed7444da9f424b8b5a37e6c9d06c0110d824`. The build produced
`elevenlabs_api_tool-0.1.0-py3-none-any.whl` (133,785 bytes) and
`elevenlabs_api_tool-0.1.0.tar.gz` (135,485 bytes).

Artifact SHA-256: wheel `0d2b1898fc8301f129cba0af3307b55e9d7d5c9d3c6028cfe60d3fd3b9bb48a7`;
sdist `aa19f5ace6d0c9c1b4cd6c5ffd6fb1ab601cb757018e46d2e912a47b5868145e`.

Both archives contain `generated_inventory.py` and the source-only
`inventory_generator.py`; neither contains `openapi.json`, `.env`, `.state`, cache, or
private-workspace paths. The installed CLI was run from a fresh Python 3.12 virtual
environment after installing the wheel and its declared `requests` dependency:
`--version`, `--help`, offline `auth check`, `voices list`, `models list`, `usage get`,
`tts synthesize --voice-id voice-123 --text hello --out output.mp3`, sensitive-output
`auth check --out auth.json`, WSS `stt realtime`, and both multi-context WSS plans all returned deterministic plan output
with no provider calls. A generated ElevenAgents command was also exercised with
`conversational-ai-agents-summaries get --out agents.json`. The installed CLI imports the
generated runtime ledger directly. `inventory_generator.py` is a source-maintenance module,
not a supported installed CLI surface; regeneration and drift checks run from the source
checkout where `openapi.json` and the generated docs are present.

The final installed smoke also covered `conversational-ai-triage-tickets workspace-list
--out triage.json`, which produced a sensitive read plan and enforced file-only output.
The clean Python 3.12 environment used the wheel plus locally available declared dependency
packages; no authenticated or live provider call was made.
