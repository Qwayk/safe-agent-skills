# Onboarding (non-technical)

This CLI runs locally and needs an OpenAI API key for live reads. Current writes create reviewable plans, then require explicit no-snapshot approval before OpenAI HTTP when no saved snapshot is available.

Important: keep your `.env` file private and never paste it into chat.

## Step 1: Create the `.env` file

1) Copy `.env.example` to `.env` in the tool folder.
2) Fill the following keys with values from your OpenAI account:
   - `OPENAI_API_BASE_URL`: `https://api.openai.com/v1` or the private endpoint your org provides.
   - `OPENAI_API_KEY`: the key you created for API access (use the same one you use for `curl https://api.openai.com/v1/models`).
   - `OPENAI_ORGANIZATION_ID`: optional, include it if your admin enforces org scoping.
   - `OPENAI_PROJECT_ID`: optional, include it if you only want to act within a specific OpenAI project.
   - `OPENAI_TIMEOUT_S`: optional request timeout in seconds (default `30`).

## Step 2: Get an OpenAI API key

1) Log in to https://platform.openai.com/.
2) Open the “API keys” page from the left nav.
3) Click “Create new secret key”, give it a descriptive name, and copy the value immediately.
4) Paste the key value into the `OPENAI_API_KEY` field in `.env`. Do not paste it anywhere else.

If your account uses org/project scoping, copy the matching values from the “Organizations” or “Projects” pages into `OPENAI_ORGANIZATION_ID`/`OPENAI_PROJECT_ID`.

## Step 3: Run the first check

1) With the `.env` file populated, run `openai-api-tool --output json --version`. It should print the CLI version without contacting the network.
2) Ask the AI agent to run `openai-api-tool auth check --output json` to verify credentials (the agent will do this for you before any other command).

## Step 4: What to ask your AI agent (examples)

Ask the agent to:
- “List the available OpenAI operations, show me a dry-run plan for one, and tell me which flags would be needed for an apply attempt.”
- “Inspect my files bucket, show me a plan for uploading a file, and save the plan to `plan.json` so I can review.”
- “Prepare a spend-money operation plan, require `--ack-spend-money`, and confirm the current apply attempt will require explicit no-snapshot approval before OpenAI HTTP.”

## Step 5: If something fails

Common issues:
- Missing/incorrect `.env` values. Re-run `openai-api-tool auth check --output json` to confirm the local config shape.
- API key lacks the necessary role. Check your OpenAI admin console and create an admin key if needed.
- Network restrictions. Confirm the CLI can access `https://api.openai.com` from the machine before running with `--live`.
