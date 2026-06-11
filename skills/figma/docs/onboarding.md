# Connect your Figma account

Use this page when you want the Figma skill ready for real work.

You do not need to understand the whole Figma API first. You only need the right token mode, a small local `.env` file, and the file, team, or project IDs for the work you actually want to do.

Keep `.env` private. Never paste token values into chat.

## Step 1: Copy `.env.example` to `.env`

Fill these first:

- `FIGMA_BASE_URL`
- `FIGMA_AUTH_MODE`
- `FIGMA_ACCESS_TOKEN` if you use `personal` or `plan` mode
- `FIGMA_TIMEOUT_S` only if you want a custom timeout

## Step 2: Pick one auth mode

Use exactly one mode:

- `personal` for a normal personal access token
- `oauth` for an OAuth token JSON file stored at `.state/token.json`
- `plan` for plan-scoped token flows when the job needs that Figma mode

If you use OAuth, save the token file locally with:

```bash
figma-safe-agent-cli auth token set --file /path/to/token.json
figma-safe-agent-cli auth token status
```

## Step 3: Run the built-in setup check

```bash
figma-safe-agent-cli onboarding
figma-safe-agent-cli auth check
```

If the command succeeds, the skill can make authenticated calls with your current config.

If it says blocked, go to [Troubleshooting](troubleshooting.md) before trying live work.

## Good first asks

Start with safe reads first:

- "Show me what this Figma token can safely inspect."
- "List the file, project, component, and library reads that are already available."
- "Preview a comment or webhook change, but do not send it yet."

## If setup is blocked

Most onboarding blocks are simple:

- missing `.env` fields
- wrong auth mode for the token you have
- OAuth token JSON missing or expired
- file, team, project, or plan-level access limits in the Figma account

`figma-safe-agent-cli auth check` tells you which of those is blocking.
