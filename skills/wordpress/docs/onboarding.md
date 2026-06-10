# Onboarding (non-technical)

This tool runs on your computer, and connects to your WordPress site using a WordPress **Application Password**.

Goal: use a dedicated WordPress user with the **minimum permissions** needed, so the tool can help with content workflows without having full admin power.

## Step 1) Create a dedicated WordPress user (recommended)

In WordPress Admin:

1) Go to **Users → Add New**.
2) Create a new user for the tool (example name: “Content Assistant”).
3) Choose the lowest role that can do your job:
   - If you only need to work on that user’s own posts: **Author**
   - If you need to edit many existing posts: often **Editor**
4) Avoid using an **Administrator** account unless you truly need it.

## Step 2) Create an Application Password

In WordPress Admin:

1) Go to **Users → Profile** for the tool user.
2) Find **Application Passwords**.
3) Create a new application password (name it something like “wordpress-api-tool”).
4) Copy the generated password and store it safely.

## Step 3) Fill the local `.env` file (on your machine)

In the tool folder, copy `.env.example` to `.env` and fill:

- `WP_BASE_URL` (example: `https://example.com`)
- `WP_USERNAME` (the tool user’s username)
- `WP_APP_PASSWORD` (the application password you created)

Important:
- Keep `.env` private. Do not paste it into chat or share it publicly.

## Step 4) What to ask your AI agent (examples)

These are plain-English requests you can give to your agent. The agent should run a dry-run first, then ask for confirmation before applying changes.

Discovery / targeting (read-only):

- “Confirm the tool is connected, then find 10 posts mentioning ‘X’ and summarize what you found.”
- “Search the site for ‘X’ and show me the top matches (even if they aren’t posts).”
- “List the site’s categories and tags, then help me map them to my target system.”
- “List comments for post ‘Y’ so I can decide what to migrate.”
- “List images used in the post with slug ‘Y’ and tell me which ones have missing alt text.”

Bulk content hygiene (safe-by-default):

- “I have a spreadsheet of image IDs and captions. Propose a bulk update to Media Library captions and show me the preview.”
- “Standardize image captions to this format: … (don’t apply until I approve).”
- “Plan a bulk download of media files to my computer (from a list of IDs and/or URLs), then download only after I approve.”
- “Set the categories and tags for the post ‘Y’, but show me exactly what would change before applying.”

Safe edits inside post content:

- “Preview how you would update visible image captions inside the post ‘Y’ and show me a diff. Apply only after I approve.”

Workflow:

- “Change post ‘Y’ from draft to publish only if it’s currently draft. Dry-run first.”

Migration support:

- “Generate a tracking CSV from my WordPress export XML and tell me where it was written.”

## If something fails

- If auth fails, the most common causes are:
  - wrong username or application password
  - a security plugin/host blocking REST API auth headers
  - `WP_BASE_URL` pointing to the wrong site/domain
- See `docs/troubleshooting.md` for symptoms and fixes.
