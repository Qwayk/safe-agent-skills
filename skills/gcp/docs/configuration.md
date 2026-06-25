# Configuration

Configuration means the private settings the tool reads before it starts a command. For this Google Cloud skill, configuration is mainly local guardrails and quota context, not a replacement for Google authentication.

Most users only need one file: `.env`. Put private values in `.env` or the `--env-file` and keep them out of chat and Git.

Configuration does not replace Google Cloud authentication. You still need ADC from `gcloud auth application-default login` or a service account file, a project or quota context, and IAM permission for the resource you want to read.

A good first configuration check is: confirm the quota project and allowlists match the project, folder, billing account, and region you are about to inspect, then stop before any planned change if the target is not listed.

## Files

- `.env.example`: copy this to `.env` if you want local defaults or guardrails
- `.state/runs/`: local run records, plans, receipts, and summaries

## Environment variables

The current GCP runtime uses these settings:

- `GCP_QUOTA_PROJECT`: optional billing or quota project
- `GCP_ALLOWED_PROJECTS`: comma-separated project IDs the tool may touch
- `GCP_ALLOWED_FOLDERS`: comma-separated folder IDs the tool may touch
- `GCP_ALLOWED_ORGANIZATIONS`: comma-separated organization IDs the tool may touch
- `GCP_ALLOWED_BILLING_ACCOUNTS`: comma-separated billing account IDs the tool may touch
- `GCP_ALLOWED_REGIONS`: comma-separated region names the tool may touch; zones such as `europe-west1-b` are checked as `europe-west1`, and common `locations/...` resource names are checked too
- `GCP_TIMEOUT_S`: optional timeout in seconds, default `30`

The current runtime does not need a separate API base URL or a token placeholder in `.env`.

## Project and quota context

Set `GCP_QUOTA_PROJECT` when Google should charge quota to a specific project:

```bash
GCP_QUOTA_PROJECT=QUOTA_PROJECT_ID
```

You can also pass `--quota-project QUOTA_PROJECT_ID` on a command or set the ADC quota project with `gcloud auth application-default set-quota-project QUOTA_PROJECT_ID`.

The quota project is not always the same as the target resource project. For a first setup, use the project you expect to inspect unless your Google Cloud admin tells you to use a separate quota project.

## Value format

- Use commas between allowlist entries.
- Leave an optional field blank if you do not want to set it.
- Put the real values in `.env`, not in chat.

## OS environment override

OS environment variables override values from the env file.
This is useful in CI or when running in containers.

For normal local use, `.env` is the easiest path.

## What a good setup looks like

A good first setup has:
- ADC available from `gcloud` or `GOOGLE_APPLICATION_CREDENTIALS`
- a quota project that matches the project you expect Google to use for quota
- allowlists that include only the projects, folders, organizations, billing accounts, and regions you want the tool to touch
- no copied secrets in chat, terminal history, committed files, or shared screenshots

If the tool can read local config but live Google Cloud reads fail, check IAM permission and enabled APIs before changing these settings.
