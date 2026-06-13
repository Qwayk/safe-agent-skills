# Connect your Freepik account

Freepik needs a local API key before an agent can search assets, review previews, check licenses, or prepare download plans.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a search and preview links before asking for licensed downloads or saved files.

## Step 1. Get a Freepik API key

Open your Freepik account dashboard, find the API section, and create an API key.

The exact dashboard steps can change over time, so use Freepik's current account UI if the labels move.

## Step 2. Fill your local `.env` file

In the tool folder, copy `.env.example` to `.env` and fill these values:

- `FREEPIK_API_BASE_URL`
- `FREEPIK_API_KEY`

Keep the default base URL unless Freepik support tells you to use something else.

## Step 3. Optional: choose your local output paths

If you want stable local paths for downloaded files and the inventory CSV, create a small project config JSON and pass it with `--config`.

Useful keys:

- `downloads_dir`
- `inventory_csv`

## Step 4. Ask your agent to check access first

Before any real work, ask for a safe auth check.

Example:

- "Check that my Freepik skill is connected, then show me a short photo search for mushroom pasta."

## Step 5. Ask for the real job

Good next requests:

- "Search for 40 recipe photos for mushroom pasta, exclude AI best-effort, and give me a shortlist."
- "Preview the top 10 so I can pick the final IDs."
- "Prepare download plans only for the IDs I approved and show me the no-snapshot approval that live download would need."
- "Use my jobs CSV to prepare a careful batch download pass, and only apply after I confirm the final list."

## If something fails

Common causes:

- missing or invalid API key
- Freepik plan or quota limits
- missing AI flags on a resource detail response, which makes the tool refuse download for safety
- missing `--ack-no-snapshot` on a licensed live download

See [Troubleshooting](troubleshooting.md) for common fixes.
