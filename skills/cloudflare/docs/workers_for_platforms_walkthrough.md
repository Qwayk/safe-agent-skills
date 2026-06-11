# Workers for Platforms walkthrough (safe, end-to-end)

This walkthrough is written for non-technical users and the AI agent helping them.

Goal: manage **Workers for Platforms** (your “customer Workers”) safely:
- preview (dry-run plan)
- explicit approval before any write
- verify after apply
- never print sensitive outputs (tokens/code) to the terminal

If you want the full endpoint list, see:
- `docs/api_coverage_workers_platform.md` (search for “Workers for Platforms”)

## What you need (non-secret)

Your agent will usually ask for these (or discover them safely):
- Your Cloudflare `account_id`
- A “dispatch namespace” name (a container for customer Workers)
- A customer Worker `script_name`

You do **not** need to share your API token in chat. Keep it in your local `.env`.

## Safety rules you should expect

- The agent should **plan first** for any change (no writes by default).
- The agent should only apply after you explicitly approve (you’ll see `--apply --yes` in details mode).
- Anything that returns **code** or a **token** is **file-only**:
  - saved to a local file with `--out …`
  - never printed to the terminal
- Some operations can return a temporary upload token (JWT). Those require an extra confirmation:
  - `--ack-irreversible`

## Common outcomes you can ask for (plain English)

- “Create a dispatch namespace for customer Workers.”
- “List customer Workers in my dispatch namespace.”
- “Upload (or replace) a customer Worker script.”
- “Add a secret binding to a customer Worker (I will provide the secret value from a local file).”
- “Tag a customer Worker so we can track ownership/environment.”
- “Start an assets upload session and save the temporary upload token to a file (never show it).”
- “Delete a customer Worker (after showing me a dry-run plan).”

## Step-by-step: typical setup flow

### Step 1: confirm what exists (read-only)

Your agent should:
1) list dispatch namespaces
2) list scripts inside the target namespace
3) fetch one script’s settings/tags/bindings (metadata only)

If you don’t have a namespace yet, move to Step 2.

### Step 2: create a dispatch namespace (plan → apply)

Your agent should:
1) produce a dry-run plan for creating the namespace
2) ask you to confirm
3) apply and then verify by re-fetching the namespace

### Step 3: upload or update a customer Worker (plan → apply)

Uploads are writes, so the agent should plan first and apply only after approval.

Notes:
- “Upload Worker module” typically uses a multipart/form-data request (your agent can generate the multipart spec file for you).
- If you’re updating only settings/tags/secrets, those are separate operations.

### Step 4: manage secrets safely (plan → apply; never print values)

Cloudflare’s API returns secret **metadata**, not secret **values**.

Your agent should:
- store secret values only in a local file (not in chat)
- call the “add secret” operation using a body file
- verify by listing secret bindings (metadata only)

### Step 5 (optional): assets upload session (extra safety)

“Create Assets Upload Session” can return a **temporary upload token**.

Your agent must:
- write the response to a local file (`--out …`)
- never print it to the terminal
- require your explicit approval (`--apply --yes`) plus the extra confirmation (`--ack-irreversible`)

## Details mode: the exact operations your agent will use

This tool supports all Workers for Platforms operations via `cloudflare-api-tool operations <area> <op_key>`.

Common operations (under area `workers_platform`; `op_key` matches the Cloudflare `operationId` when present):
- Create namespace: `namespace-worker-create`
- List scripts in namespace: `namespace-worker-list-scripts`
- Upload worker module: `namespace-worker-script-upload-worker-module`
- Put script content (sensitive): `namespace-worker-put-script-content` (file inputs; writes)
- Add secret binding: `namespace-worker-put-script-secrets`
- Put tags: `namespace-worker-put-script-tags`
- Create assets upload session (sensitive write result): `namespace-worker-script-update-create-assets-upload-session`

If you want the agent to “stay inside” Workers for Platforms only, ask them to:
- use operations that have the `Workers for Platforms` tag (visible in `operations list/show` output and in `docs/api_coverage_workers_platform.md`)
