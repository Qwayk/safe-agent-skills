# Authentication

The tool supports three auth modes:

- `personal` (default): uses `FIGMA_ACCESS_TOKEN` as `X-Figma-Token`.
- `oauth`: uses `FIGMA_ACCESS_TOKEN` or an OAuth `access_token` loaded from `.state/token.json`, and sends `Authorization: Bearer`.
- `plan`: uses `FIGMA_ACCESS_TOKEN`; `/v1/me` smoke checks are intentionally skipped because plan tokens have different token checks.

## Personal or plan mode

1. Set in `.env`:
   - `FIGMA_AUTH_MODE=personal` (or `plan`)
   - `FIGMA_ACCESS_TOKEN=<your token>`
2. Run:

```bash
figma-safe-agent-cli auth check
```

## OAuth mode

1. Set `FIGMA_AUTH_MODE=oauth`.
2. Place a JSON token file from your OAuth flow:

```bash
figma-safe-agent-cli auth token set --file /path/to/token.json
```

This stores a normalized copy under `.state/token.json` near your `.env`.
3. Confirm file status only:

```bash
figma-safe-agent-cli auth token status
```

4. Run live auth check:

```bash
figma-safe-agent-cli auth check
```

`auth check` uses `GET /v1/me` for personal and oauth modes, and reports blocked state if token lookup or probe fails. It does not return token values.

## Token hygiene

- Never share token values in logs or prompt text.
- Secrets are redacted in tool output and audit logs.
