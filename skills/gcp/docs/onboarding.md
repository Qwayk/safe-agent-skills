# Set up Google Cloud access

Choose the Google account or service account you want to use, then test it with one small read in a project you recognize. For that first read, use an account that already has permission to view the resource.

## Connect your account

Google client libraries look for Application Default Credentials (ADC) on your machine. This CLI asks for the `cloud-platform` scope. If you’re using your own account, run:

```bash
gcloud auth application-default login
```

If you already use a local service account file, set `GOOGLE_APPLICATION_CREDENTIALS` to its path. Keep service account files, OAuth files, tokens, keys and private settings on your machine. [Google’s ADC guide](https://docs.cloud.google.com/docs/authentication/application-default-credentials)

A quota project is where Google counts certain API requests for quota and billing. It can differ from the project that holds your resource. If you need to set the quota project on your Google credentials, run:

```bash
gcloud auth application-default set-quota-project QUOTA_PROJECT_ID
```

Use a project you expect to pay for those requests. You can also set `GCP_QUOTA_PROJECT` in your settings or pass `--quota-project QUOTA_PROJECT_ID` for one command. [Google’s quota project guide](https://docs.cloud.google.com/docs/quotas/set-quota-project)

## Set limits for this tool

Use `.env` for optional settings or pick a different file with `--env-file`. The setup helper can create the file for you. It keeps any file that already exists and shows the next command with the same settings path. Add `--no-write-env` to see the instructions without creating a file.

```bash
qwayk-gcp-safe-agent-cli onboarding
qwayk-gcp-safe-agent-cli --env-file "google cloud.env" onboarding
```

| Setting | What it does |
|---|---|
| `GCP_QUOTA_PROJECT` | Picks the quota project for requests. |
| `GCP_ALLOWED_PROJECTS` | Lists the project IDs this tool may touch. |
| `GCP_ALLOWED_FOLDERS` | Lists the folder IDs this tool may touch. |
| `GCP_ALLOWED_ORGANIZATIONS` | Lists the organization IDs this tool may touch. |
| `GCP_ALLOWED_BILLING_ACCOUNTS` | Lists the billing account IDs this tool may touch. |
| `GCP_ALLOWED_REGIONS` | Lists allowed regions. The tool checks a zone like `europe-west1-b` as `europe-west1` and checks common `locations/...` resource names. |
| `GCP_TIMEOUT_S` | Sets the request timeout in seconds. The default is 30. |

Use commas between entries, leave optional values blank, and keep the settings file out of Git. Environment variables take priority over values in the file. Keep local run records under `.state/runs/` private too.

## Check access

```bash
qwayk-gcp-safe-agent-cli --output json auth check
```

This checks Google credentials and shows the project or quota project Google returned, when available. Then follow [the quickstart](quickstart.md) to check whether that account can read the service and resource you picked. Google IAM controls those permissions. Before asking anyone to approve a change, follow [the write approval steps](safety_model.md).

## Fix a connection problem

| What you see | What to check |
|---|---|
| `gcloud: command not found` | Install Google Cloud CLI or check that it is on your `PATH`. Run `gcloud --version`. If this machine uses a service account file, check its local path instead. |
| `DefaultCredentialsError` | Run the ADC sign-in again or check where `GOOGLE_APPLICATION_CREDENTIALS` points. |
| Quota or billing error | Check the quota project, its billing setup and whether your Google identity can use it. |
| Permission error on a read | Check the exact target, whether the API is enabled and whether your account has the read permission for that resource. |
| The tool refuses the target | Check the project, folder, organization, billing account or region in the input against your settings. |
| The tool cannot prepare a write plan for this identity | Use an ADC sign-in with a stable Google user credential or a named service account, then make a new plan. |

Start with the exact error and the same small read. Use `--verbose` for request timing or `--debug` for a Python stack trace when investigating the code. Keep any private values out of shared output. [Google’s ADC troubleshooting guide](https://docs.cloud.google.com/docs/authentication/troubleshoot-adc)
