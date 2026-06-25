# Authentication

Authentication means proving to Google that this CLI is allowed to read or change your cloud resources.

For this skill, authentication is meant to be local: use Google Application Default Credentials, keep credential files on the machine, and do not paste secrets into chat. The normal path here is usually ADC with the `cloud-platform` scope. ADC is a local Google sign-in file or service account file that official Google client libraries find automatically.

Authentication is only one part of setup. The tool also needs a project or quota context, and the signed-in user or service account needs enough IAM permission for the read you want. IAM is Google Cloud's access-control system.

A good first auth check is: confirm ADC is available, name the quota project if one is set, then run one small read against a project you recognize before planning any change.

## Normal path

If you are using your own Google account on a workstation, run:

```bash
gcloud auth application-default login
```

If you are using a service account file, keep `GOOGLE_APPLICATION_CREDENTIALS` set to that file before you run the CLI.

The CLI will then call Google APIs through ADC and attach the `cloud-platform` scope.

If `gcloud` is missing, install the Google Cloud CLI before using the workstation sign-in flow. If you cannot install it on that machine, use a service account ADC file that is already stored outside chat and set `GOOGLE_APPLICATION_CREDENTIALS` to its local path.

## Option 2: Quota project

If Google Cloud should bill or count quota against a different project, set it with one of these:

```bash
gcloud auth application-default set-quota-project QUOTA_PROJECT_ID
```

or:

- `GCP_QUOTA_PROJECT=QUOTA_PROJECT_ID`
- `--quota-project QUOTA_PROJECT_ID`

The quota project is the project Google uses for billing and quota checks on client-based API calls.

Use a project you control and expect to pay for quota. If the quota project is wrong, Google may reject the request even when your credentials are valid.

## Permission check

After ADC and quota context are ready, the first useful check is:

```bash
qwayk-gcp-safe-agent-cli --output json auth check
```

That proves the local credential path can be found. It does not prove every Google Cloud read will work. A real service read still depends on the target project, whether the Google API is enabled, and whether the signed-in identity has the needed IAM role.

## Manual token files

The current GCP source tool does not use a manual token file for normal operation.

Use ADC instead. If a future flow needs a copied token, it must be added as a specific documented command with the same redaction and storage tests.

## Safety reminders

- Never commit `.state/`.
- Keep `.env`, service account JSON files, and OAuth files out of chat.
- Never print tokens in logs.
- Never paste keys, tokens, or OAuth files into chat.
- If `auth check` fails with `DefaultCredentialsError`, the machine does not have ADC yet.
- Live Google Cloud account behavior remains unverified until someone runs a real safe-target read with a real account.
