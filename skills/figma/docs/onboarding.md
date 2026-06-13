# Connect your Figma account

Figma needs a local token or plan-based access before an agent can inspect files, nodes, teams, projects, or comments.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a file or access check and confirm the file, team, or project ID before asking for edits or exports.

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
