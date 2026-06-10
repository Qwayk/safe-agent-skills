# Onboarding (non-technical)

You can use this tool without deep technical knowledge.
It runs on your machine and only needs a small `.env` file with your token settings.

## Step 1: Set up `.env`

1. Copy `.env.example` to `.env`.
2. Fill values for:
   - `FIGMA_BASE_URL`
   - `FIGMA_AUTH_MODE`
   - `FIGMA_ACCESS_TOKEN` (optional only if you use OAuth token file mode)
   - `FIGMA_TIMEOUT_S` (optional)
3. Keep `.env` private. Never paste token values into chat.

## Step 2: Pick your auth mode

Use exactly one mode:
- `personal` for personal account / PAT workflows.
- `oauth` to use an OAuth token JSON file stored at `.state/token.json`.
- `plan` to use plan tokens for plan-scoped endpoints.

## Step 3: Verify you are connected

```bash
figma-safe-agent-cli auth check
```

If the command succeeds, the tool can make authenticated calls with your current config.

If it says blocked, follow the hints in `docs/troubleshooting.md` before continuing.

## What to ask an agent

Use read-only checks first:
- “Show what Figma operations this tool supports for my account.”
- “Find safe target files and return a preview only.”
- “Create a plan for the exact changes, then hold until I approve.”

## If setup is blocked

Most onboarding blocks are:
- Missing `.env` fields.
- Wrong auth mode for the requested use.
- OAuth token JSON missing or expired.
- Team-level permission limits in the Figma account.

The command `figma-safe-agent-cli auth check` tells you which of those is blocking.
