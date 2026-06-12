# Connect your YouTube account

This tool runs on your computer and connects to the **YouTube Data API v3** using credentials you keep locally.

You do not need to be technical. You can ask an AI agent to do the work, and the agent should come back with a safe read, a dry-run plan for higher-risk actions, and proof of what really happened.

Keep these private:
- your `.env` file
- your OAuth client secrets file
- your local `.state/token.json` file if you already have one

## Step 1: Choose the access mode you need

- **API key** is enough for many public read-only requests.
- **OAuth** is needed for private reads, uploads, and most write-capable actions.

If you only want public channel research, start with an API key. Choose OAuth when you need private channel data, uploads, or changes.

## Step 2: Create the credentials in Google Cloud

Open Google Cloud Console, select or create a project, and enable **YouTube Data API v3**.

### Option A: API key for public reads

1. Go to **APIs & Services -> Credentials**.
2. Create an API key.
3. Keep it private for your local `.env` file.

### Option B: OAuth for private reads and writes

1. Go to **APIs & Services -> Credentials**.
2. Create an **OAuth client ID**.
3. Choose **Desktop app**.
4. Download the client secrets JSON file to your machine.

## Step 3: Fill the local `.env` file

In the tool folder:

1. Copy `examples/example.env` to `.env`. In a source checkout, `.env.example` may also be available.
2. Open `.env` in a text editor.
3. Fill what you need:
   - `YOUTUBE_API_KEY=...` for public reads
   - `YOUTUBE_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client_secrets.json` for OAuth
   - optional scope override only when you really need a different scope set

Keep the default base URL unless you have a very unusual setup.

## Step 4: Know the current OAuth limit

This part matters:

- `youtube-api-tool auth login --console` validates the OAuth setup and shows the planned token-write action, but it does **not** write `.state/token.json` yet.
- `youtube-api-tool auth token set --file token.json` also stops at the plan/refusal step today.

If you already have a valid token JSON from a separate approved flow, place it at `.state/token.json` next to your `.env` so the read-only token checks can see it.

## Step 5: Ask for safe first checks

These are good first requests for your agent:

- “Confirm the YouTube skill is connected and show me the safe read options first.”
- “Resolve this channel from the handle and show the latest uploads.”
- “Plan a channel export to a local folder, but do not write anything yet.”
- “Plan a video upload and stop before any upload or metadata change happens.”

## What success looks like

Setup is ready when `auth check` can see either your API key or your local OAuth token, and your agent can run a safe plan such as channel resolve without printing secrets.

## If something fails

The most common issues are:
- missing or wrong values in `.env`
- using an API key for an endpoint that really needs OAuth
- missing scopes or channel permissions
- expecting the built-in OAuth helpers to write the token file automatically in this build

See [Troubleshooting](troubleshooting.md) for the usual error paths and fixes.
