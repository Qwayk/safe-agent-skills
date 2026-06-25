# Quickstart

Start with a result you can recognize: the Google Cloud identity, the project or quota context, and one small read such as Compute Engine instances, enabled services, a storage bucket list, or Cloud Run services. If the target looks wrong, stop before asking for a change.

Need more ideas? See [Useful Google Cloud asks](use_cases.md). Need setup help? See [Connect Google Cloud safely](onboarding.md).

A good first ask is:

> Check that Google Cloud access is connected, tell me which project or quota context you can see, run one safe read if permissions allow, and stop before any live change.

## What you will do first

1. Make sure the local tool can run.
2. Confirm Google Application Default Credentials are available.
3. Optionally check the generated service inventory without touching a cloud resource.
4. Run one small read against a project and zone you recognize.
5. Stop before any write, IAM change, public exposure change, delete, service enablement, or cost-sensitive action.

## 1. Install for local source use

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

## 2. Make sure Google auth is ready

If you use your own Google account on this machine:

```bash
gcloud auth application-default login
```

If you already use a service account file, keep `GOOGLE_APPLICATION_CREDENTIALS` set to that local file path. Do not paste the file into chat.

## 3. Run one small first read

Start with a project and zone you recognize. Save this as `input.json`:

```json
{
  "path": {
    "project": "my-gcp-project",
    "zone": "us-central1-a"
  },
  "query": {
    "maxResults": 10
  }
}
```

Then run:

```bash
qwayk-gcp-safe-agent-cli compute instances-list --input-json input.json
```

Replace `my-gcp-project` and `us-central1-a` with real values from your account. If your identity has permission and Compute Engine is enabled, the result should show instances from that zone. If the result is empty or blocked, check the project, zone, enabled API, IAM permission, quota project, and allowlists before planning any change.

## 4. Stop before anything risky

Reads can run without apply flags. Anything that changes Google Cloud should start with a dry-run plan and wait for review.

For example, a delete-like command must be planned first:

```bash
qwayk-gcp-safe-agent-cli compute instances-delete --input-json input.json --plan-out plan.json
```

Do not apply a plan until a reviewer has checked the project, region or zone, service, operation, input, risk, and required acknowledgement flags.

## Optional setup checks

If this is the first run on the machine, run onboarding and then check credentials:

```bash
qwayk-gcp-safe-agent-cli onboarding
qwayk-gcp-safe-agent-cli --output json auth check
```

The auth check proves that the local credential path can be found. It does not prove that every live Google Cloud read will work.

To check the packaged generated service map without touching a Google Cloud account, run:

```bash
qwayk-gcp-safe-agent-cli --output json inventory summary
```

This reads the packaged coverage inventory only. It is useful for seeing what the source tool knows how to call, but it does not touch your Google Cloud account.

## What a useful first result includes

- which Google Cloud identity and quota context were used
- which project, region, zone, service, and operation were checked
- whether the read succeeded, returned nothing, or was blocked
- what the result means in normal words
- what is safe to inspect next
- whether any plan, receipt, or saved output was written

## Where to go next

- For real examples, read [Useful Google Cloud asks](use_cases.md).
- For setup details, read [Connect Google Cloud safely](onboarding.md).
- For exact command options, read [Command guide](command_reference.md).
- For approval rules and limits, read [Review before changes](safety_model.md).
