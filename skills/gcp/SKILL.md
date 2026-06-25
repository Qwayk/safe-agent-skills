---
name: gcp
description: Use when the agent needs to inspect Google Cloud or prepare careful Google Cloud changes through qwayk-gcp-safe-agent-cli.
---

# GCP Safe CLI

Trigger this skill when the user wants help with Google Cloud projects, IAM access, servers, IP addresses, storage buckets, Cloud Run, Cloud SQL, networking, logs, enabled services, billing context, quota context, or a planned infrastructure change.

Start with a safe read. A good first move is to check Google Cloud access, name the project or quota context, run one small read the user can recognize, explain the result in normal words, and stop before any live change.

## Access

Google Cloud access uses Application Default Credentials with the `cloud-platform` scope.

Normal setup paths:

- `gcloud auth application-default login`
- a local service account file through `GOOGLE_APPLICATION_CREDENTIALS`

Optional guardrails include `GCP_QUOTA_PROJECT` or `--quota-project`, plus allowlists for projects, folders, organizations, billing accounts, and regions.

Never ask the user to paste `.env`, service account JSON, OAuth files, tokens, or keys into chat.

## Safe workflow

1. Run `qwayk-gcp-safe-agent-cli --output json auth check`.
2. Run `inventory summary` only to inspect packaged coverage. For live verification, run one known project service read, such as Compute Engine instances, enabled services, storage buckets, or Cloud Run services.
3. Explain the result in normal words before showing raw output.
4. For any write, create a dry-run plan first.
5. Apply only from the reviewed saved plan with `--plan-in`, `--apply`, and `--yes`.
6. Add `--ack-no-snapshot` or `--ack-irreversible` when the runtime requires it.
7. After live work, report whether verification was full read-back verification or limited provider-response verification.

## Example safe reads

- `qwayk-gcp-safe-agent-cli --output json auth check`
- `qwayk-gcp-safe-agent-cli --output json inventory summary`
- `qwayk-gcp-safe-agent-cli compute instances-list --input-json input.json`

## Stop or refuse

Stop before acting when:

- the project, region, zone, service, or resource target is unclear
- IAM blocks the read or change
- the target is outside configured allowlists
- the user asks for a raw request, arbitrary URL call, or permission bypass
- the request could delete, expose, spend, alter IAM, change networking, or affect production without a reviewed plan

## Honest limits

Local tests, generated coverage, mocked examples, and shape examples prove command shape and safety behavior only. Live Google Cloud account behavior has not been verified. Treat the first real account read as a live verification run and say that limit clearly.

Do not promise rollback, backup, restore, or undo unless the exact Google Cloud operation supports that provider action and the user has reviewed a plan for it.
