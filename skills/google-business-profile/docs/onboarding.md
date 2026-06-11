# Onboarding

Use this page when you want the shortest safe setup path for Google Business Profile.

This skill runs on your machine and uses Google OAuth credentials you keep locally.
Do not paste secrets into chat.

## Step 1: Create the local `.env` file

In the tool folder:

1. Copy `.env.example` to `.env`.
2. Open `.env` in a text editor.
3. Add the path to your Google OAuth client secrets file.

The main field you will usually need is:

```text
GBP_OAUTH_CLIENT_SECRETS_FILE=/absolute/path/to/client-secrets.json
```

If you want the tool to create or refresh the starter file for you, run:

```bash
google-business-profile-safe-cli onboarding
```

## Step 2: Sign in with Google OAuth

Run:

```bash
google-business-profile-safe-cli auth login --console
```

This stores the local token state beside your `.env` file.

## Step 3: Check access before real work

Ask your agent to start with safe checks like:

- "Check the Google Business Profile skill is connected."
- "List the accounts and locations I can access."
- "Show me what is safe to review before we plan any changes."

If you want to run the first checks yourself:

```bash
google-business-profile-safe-cli auth check
google-business-profile-safe-cli account-management accounts list
```

## Step 4: First requests to give your agent

These are good first requests in plain English:

- "List my Google Business Profile accounts and locations."
- "Review this location and flag anything incomplete or risky."
- "Show me recent reviews and verification status for this location."
- "Plan the change first and stop before any live Google Business Profile write."

## Step 5: If something fails

The most common setup problems are:

- the client secrets file path is wrong
- the Google login did not finish cleanly
- the signed-in account does not have access to the account or location you want

Use [Troubleshooting](troubleshooting.md) if the first checks fail.
