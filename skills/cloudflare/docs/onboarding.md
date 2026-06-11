# Onboarding (non-technical)

This tool runs on your computer and connects to the Cloudflare API using an API Token that you store locally.

Important:
- Your `.env` file contains secrets. Keep it private and never paste it into chat.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1) Copy `.env.example` to `.env`.
   - Alternatively: run `cloudflare-api-tool config init` to create the placeholder file.
2) Open `.env` in a text editor.
3) Fill the required fields:
   - `CLOUDFLARE_API_TOKEN=...`
   - (optional) `CLOUDFLARE_API_BASE_URL=https://api.cloudflare.com/client/v4`
   - (optional) `CLOUDFLARE_TIMEOUT_S=30`
   - (optional) split timeouts:
     - `CLOUDFLARE_CONNECT_TIMEOUT_S=10`
     - `CLOUDFLARE_READ_TIMEOUT_S=240`

## Step 2: Create a Cloudflare API Token (in the Cloudflare dashboard)

Cloudflare recommends API Tokens (least privilege). Use Cloudflare’s official guide:
- Create token: `https://developers.cloudflare.com/fundamentals/api/get-started/create-token/`
- Restrict tokens (least privilege): `https://developers.cloudflare.com/fundamentals/api/how-to/restrict-tokens/`

When choosing permissions, only grant what you need for the commands you plan to run. Most users start with read-only inventory:
- Accounts and Zones discovery
- Workers platform inventory (including scripts/dispatch/KV metadata/builds/pipelines)
- KV metadata only (never KV values)

If you plan to deploy a Workers app that uses **D1** and **KV** (common for small SaaS apps), your token also needs the D1 database permission (Cloudflare labels it as a D1 permission in the token UI).

If you plan to test Cloudflare Browser Run from this CLI, add the account permission:
- `Browser Rendering - Edit`

This tool also includes (optional) write workflows and sensitive reads, but they are **gated**:
- Writes are preview-first and require explicit approval before anything changes.
- Sensitive reads (code/KV values) require extra confirmation and only write to an explicit local output file (never printed to the screen).

If your token is least-privilege for read-only inventory, some write/sensitive commands may fail with a permissions error.
That’s expected: add only the minimum additional permissions needed for the specific command you want to run.

## Step 3: What to ask your AI agent (examples)

These are plain-English requests. The agent should start with a read-only connection check and then shortlist IDs safely.

- “Confirm the tool is connected, then list my Cloudflare accounts.”
- “Confirm the tool is connected, then run zone-create-check for my account before we onboard domains.”
- “Set my default account, then list Workers scripts and KV namespaces.”
- “Run an auth probe and tell me which permissions are missing for D1.”
- “Resolve the zone id for my domain, then list Worker routes for that zone.”

## Step 4: If something fails

The most common issues are:
- Missing/incorrect values in `.env`
- Token missing permissions for the endpoint you called
- Network/auth restrictions in the vendor account

See `docs/troubleshooting.md` and ask your agent to run a connection check first.
