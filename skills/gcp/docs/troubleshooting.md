# Troubleshooting

Start here when the tool does not connect, the output looks wrong, or the agent says it is blocked.

Most setup failures mean one of three things is missing: a Google Cloud credential path, the right project or quota context, or IAM permission for the resource you asked to read.

A good first troubleshooting ask is: "Read the exact JSON error output, explain the likely missing setting or permission in plain English, and tell me the safest next check without inventing missing data." If the target, project, or permission is unclear, stop before retrying a write or broader read.

## Common checks

Start with the exact error, the target project, the quota project, the service, and the operation. Check those facts before changing credentials, widening IAM, or retrying a larger read.

## ADC problems

Most connection issues come from missing Application Default Credentials, the wrong quota project, or permissions that do not include the target resource.

Ask your agent:

- “Check the connection and explain the problem in plain language.”
- “Tell me which setting is missing, but do not print any secret value.”

If `auth check` returns `DefaultCredentialsError`, run:

```bash
gcloud auth application-default login
```

If you already use a service account file, make sure `GOOGLE_APPLICATION_CREDENTIALS` still points at it.

If your shell says `gcloud: command not found`, the Google Cloud CLI is not installed or is not on your `PATH`. Install the Google Cloud CLI, open a new terminal, and run `gcloud --version`. If this machine should not have `gcloud`, use a service account ADC file that is already stored safely on the machine and set `GOOGLE_APPLICATION_CREDENTIALS` to that local file path.

## Quota project problems

If the tool says the quota project is wrong or missing, set one of these:

- `GCP_QUOTA_PROJECT=QUOTA_PROJECT_ID`
- `--quota-project QUOTA_PROJECT_ID`

Or update ADC directly:

```bash
gcloud auth application-default set-quota-project QUOTA_PROJECT_ID
```

If `auth check` works but a real read fails with a quota or billing message, the signed-in identity may be valid while the quota project is missing, disabled for billing, or not allowed for that API.

## IAM permission problems

If ADC works but a service read fails with a permission error, the tool is reaching Google Cloud but the signed-in identity is not allowed to read that resource.

Check:
- the project, folder, organization, billing account, region, or zone in the input
- whether the Google API for that service is enabled
- whether the user or service account has the read role for that service

For example, a Compute Engine instances read needs permission to view Compute Engine instances in the target project. Fix the Google Cloud role first, then run the same safe read again.

## Allowlist problems

If the tool refuses a target because of an allowlist, check the comma-separated values in:

- `GCP_ALLOWED_PROJECTS`
- `GCP_ALLOWED_FOLDERS`
- `GCP_ALLOWED_ORGANIZATIONS`
- `GCP_ALLOWED_BILLING_ACCOUNTS`
- `GCP_ALLOWED_REGIONS`

For `GCP_ALLOWED_REGIONS`, the tool checks normal region fields, zone fields, location fields, and common resource names such as `projects/PROJECT/locations/REGION/...`. A zone such as `europe-west1-b` is checked as region `europe-west1`.

## Request details

Use `--verbose` only when you need to see request start and end lines.

Secrets must never be printed. That includes Authorization headers, keys, and tokens.

## Error details

By default, the tool prints one structured error. That keeps the output easy for agents to read.

If you are debugging the code itself, add `--debug` to see a full Python stack trace.

## Token file problems

The current GCP source tool uses ADC instead of a copied token file.

If a command asks for a manual token file, stop and check that you are using the current GCP source tool.

## Proof limits

Local tests and `auth check` can prove that the tool and credential lookup work on the machine. They do not prove live Google Cloud account behavior for every service. Treat live behavior as unverified until a real safe-target read succeeds with the intended account, project, quota context, and IAM permissions.

## Plan and apply problems

If a write is refused, check these gates in order:

1. `--plan-in`
2. `--apply`
3. `--yes`
4. `--ack-no-snapshot` for high-risk or no-snapshot writes
5. `--ack-irreversible` for irreversible writes
