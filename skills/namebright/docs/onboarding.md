# Onboarding

Set up the account connection, then run one safe check before any live change.

## Step 1: Create `.env`

1. Copy `.env.example` to `.env`.
2. Fill:
   - `NAMEBRIGHT_CLIENT_ID`
   - `NAMEBRIGHT_CLIENT_SECRET`
   - `NAMEBRIGHT_TIMEOUT_S` (optional)

## Step 2: Check access

Run:

```bash
namebright-safe-cli onboarding
namebright-safe-cli auth check
```

## Step 3: Start with safe asks

Use questions first, not writes:
- "Check connection and list my first domains."
- "Show what needs review: expired domains or pending NameBright account pushes."
- "Prepare a plan for these updates, then wait for approval."

## Success criteria

You are ready when the agent can:
- confirm account access
- explain what it can review now
- provide a safe first read without changing anything

If setup fails, check [troubleshooting](troubleshooting.md).
