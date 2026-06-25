# Connect your Google Cloud account

Start the same way you would start a careful cloud review: choose the Google identity, confirm the project or quota context, run one small read, then stop before any change.

You do not need to learn every command first. You do need local Google Cloud access and enough IAM permission for the resource you want the agent to inspect. IAM is Google Cloud's permission system.

Keep the setup files private. Do not paste `.env`, service account JSON, OAuth files, tokens, or keys into chat.

## Before you start

- You need the Google Cloud CLI, called `gcloud`, or a service account file that is already stored safely on this machine.
- You need a Google Cloud project for the first read.
- You may need a quota project, which is the project Google uses for billing and quota checks.
- You need IAM permission for the service you want to inspect.
- If this machine can reach many projects, use allowlists before planning writes.

## Step 1: choose the Google identity

If you are using your own Google account on a workstation, run:

```bash
gcloud auth application-default login
```

If your environment uses a service account file, keep `GOOGLE_APPLICATION_CREDENTIALS` set to that local file path before running the tool.

Avoid starting with a broad admin identity unless the job truly needs it. A read-only or audit-focused identity is better for the first review.

## Step 2: set the quota project if needed

If Google should bill or count quota against a specific project, run:

```bash
gcloud auth application-default set-quota-project QUOTA_PROJECT_ID
```

You can also use `GCP_QUOTA_PROJECT` in `.env` or pass `--quota-project` on a command.

## Step 3: add local guardrails

In the tool folder:

1. Copy `.env.example` to `.env` if you want local defaults or allowlists.
2. Keep `.env` private.
3. Add the quota project if needed.
4. Add allowed projects, folders, organizations, billing accounts, or regions when the tool should refuse every other target.

The `.env` file is for local settings only. It is not for chat and it is not for Git.

## Step 4: run the setup helper

```bash
qwayk-gcp-safe-agent-cli onboarding
```

Add `--no-write-env` if you only want instructions and do not want the helper to create `.env`.

## Step 5: confirm the connection

```bash
qwayk-gcp-safe-agent-cli --output json auth check
```

A good result confirms that Application Default Credentials are available and shows the project or quota context the tool can see. This is still only a setup check. The first live Google Cloud proof is one safe read against a project and service you recognize.

## What to ask your AI agent

- "Check that Google Cloud access is connected and tell me which project or quota context you can see."
- "Show me one safe read we can run before changing anything."
- "List enabled services in this project and explain what looks worth reviewing."
- "Review IAM access and stop before any change."
- "Prepare a careful plan for this change and wait for my approval."

## What success looks like

Setup is working when the agent can:

- confirm Application Default Credentials are available
- name the project or quota project it will use
- explain whether allowlists are active
- run one read-only request that your IAM permissions allow
- stop before any live change

If auth works but a real service read fails, setup is only partly working. The usual missing piece is the target project, quota project, enabled API, IAM permission, or allowlist.

## If something fails

Start with [Troubleshooting](troubleshooting.md). Most failures mean the machine is missing Google credentials, the target project is wrong, the quota project is not accepted, the API is not enabled, IAM is too narrow, or an allowlist refused the target.

Local setup and tests do not prove live Google Cloud behavior. Treat the first successful read in your own account as the live check.
