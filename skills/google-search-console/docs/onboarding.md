# Connect your Google Search Console account

Google Search Console needs local OAuth credentials before an agent can inspect sites, search performance, sitemaps, or URL inspection data.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start by listing the Search Console sites this token can access.

## Step 1: Create the local `.env` file (on your machine)

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill the required fields:
   - Pick one auth mode and set exactly one of:
     - `GSC_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json`, or
     - `GSC_SERVICE_ACCOUNT_FILE=/absolute/path/to/service_account.json`
   - Scopes:
     - Read-only: `GSC_OAUTH_SCOPES=https://www.googleapis.com/auth/webmasters.readonly`
     - Read + write: `GSC_OAUTH_SCOPES=https://www.googleapis.com/auth/webmasters`

Optional (advanced):
- `GSC_BASE_URL=https://searchconsole.googleapis.com` (default)
- `GSC_TIMEOUT_S=30`

## Step 2: Get the API key/token (tool-specific)

Choose one auth mode.

### Option A (recommended): Installed-app OAuth

1. Go to Google Cloud Console → “APIs & Services”.
2. Enable the “Google Search Console API” for your project.
3. Go to “Credentials” → “Create credentials” → “OAuth client ID”.
4. Pick an application type that supports local login (Desktop App is the simplest).
5. Download the client secrets JSON file to your computer.
6. Set this in `.env`:
   - `GSC_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json`
7) Run login once:
   - `gsc-api-tool auth login`

### Option B (optional): Service account

1. Create a service account JSON in Google Cloud.
2. Set this in `.env`:
   - `GSC_SERVICE_ACCOUNT_FILE=/absolute/path/to/service_account.json`
3. In Google Search Console, grant the service account email access to the property you want to work on.

Note: Service accounts are not always a drop-in replacement for user OAuth. If auth fails, use Option A.

## Step 3: What to ask your AI agent (examples)

Ask your agent to start with a read-only check, then show a preview before applying changes.

- “Confirm the tool is connected, then show me what it can do on my account.”
- “Find the right targets safely (avoid guessing), then propose changes for my review.”
- “Apply these metadata updates from a spreadsheet and give me a receipt of what changed.”
- “Do a dry-run reviewed plan first. Only apply after I approve.”

## Step 4: If something fails

The most common issues are:
- Missing or incorrect values in `.env`
- Missing OAuth login (installed-app OAuth not completed)
- Wrong OAuth scopes (read-only vs write)
- Network or permission restrictions in the connected account

See `docs/troubleshooting.md` for common errors and fixes.
