# Onboarding

Use this page when you want the shortest safe setup path for OpenAI.

This tool runs locally and needs an OpenAI API key for live reads or writes.
Keep your `.env` file private, and never paste keys into chat or shell history notes.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Fill the fields you need:

```text
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=
OPENAI_ORGANIZATION_ID=
OPENAI_PROJECT_ID=
OPENAI_TIMEOUT_S=30
```

If you want the tool to create the starter file for you, run:

```bash
openai-api-tool onboarding
```

## Step 2: Get an OpenAI API key

1. Sign in to [platform.openai.com](https://platform.openai.com/).
2. Open the API keys page.
3. Create a new secret key and copy it immediately.
4. Paste it into `OPENAI_API_KEY` in `.env`.

If your account uses organization or project scoping, copy those IDs into the matching `.env` fields too.

## Step 3: Check setup before real work

Ask your agent to start with safe checks like:

- "Check the OpenAI skill is configured."
- "List the available operations before we run anything live."
- "Show me which live reads are safe to run first."

If you want to run the first checks yourself:

```bash
openai-api-tool --output json --version
openai-api-tool api ops list
openai-api-tool --output json --live auth check
```

The first two checks stay local. The last one is your first real OpenAI network read.

## Step 4: First requests to give your agent

These are good first requests in plain English:

- "List the available OpenAI operations and find the right one for this job."
- "Review my models, files, or usage safely first."
- "Prepare the write plan first and show me the approval steps."
- "For any spend-money action, save the plan and make me review it before apply."

## Step 5: If something fails

The most common setup problems are:

- the API key is missing or wrong
- the organization or project ID is wrong for this account
- the machine cannot reach the OpenAI API
- the action needs more permissions or billing access than this key has

Use [Troubleshooting](troubleshooting.md) if the first checks fail.
