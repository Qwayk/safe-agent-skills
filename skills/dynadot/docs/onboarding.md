# Connect your Dynadot account

Dynadot needs a local API key before an agent can inspect domains, renewals, DNS, name servers, and account details.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a domain list and confirm the exact domain before asking for DNS, renewal, or transfer work.

## Step 1. Get your Dynadot API key

In Dynadot:

1. Sign in to your account.
2. Open **Tools -> API**.
3. Create or reveal your API key.
4. If you have a stable IP, add an IP whitelist too.
5. Copy the key and keep it ready for your local `.env` file.

## Step 2. Fill the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill these fields:
   - `DYNADOT_API_KEY` with your real Dynadot API key
   - `DYNADOT_API_BASE_URL` and keep the default unless Dynadot tells you otherwise
   - `DYNADOT_TIMEOUT_S` only if you need a different timeout

## Step 3. Know the extra values some jobs need

- Domain pushes use a **Push Username**. Ask the receiver for that exact Dynadot push username first.
- Guided transfer runs between two Dynadot accounts need two local env files:
  - sender account as `--env-file`
  - receiver account as `--receiver-env-file`
- Transfer auth codes are sensitive. Save them to a local file instead of pasting them into chat.

## Step 4. What to ask your AI agent

Start with a read, review the preview, and only apply after you approve the exact change.

- "Check the Dynadot tool is connected and show me my active domains."
- "Flag anything expiring soon and tell me what needs attention first."
- "Preview a push of these domains to another Dynadot account, but do not apply anything yet."
- "Show me a name server diff for these domains before any bulk change."
- "Plan the transfer run and explain whether this job needs no-snapshot approval before it can go live."

## If something fails

Common causes:
- missing or wrong values in `.env`
- API key restrictions or IP whitelist mismatch
- wrong receiver push username
- sender and receiver env files mixed up during a transfer workflow

See [Troubleshooting](troubleshooting.md) for symptoms and fixes.
