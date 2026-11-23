---
name: gcp
description: Use when the user wants to inspect Google Cloud or plan and apply an approved change with qwayk-gcp-safe-agent-cli.
---

# Google Cloud

Use this skill for Google Cloud projects, IAM, servers, IP addresses, storage, Cloud Run, Cloud SQL, networking, logs, enabled APIs, quota, billing and infrastructure changes.

1. Run `qwayk-gcp-safe-agent-cli --output json auth check`. Google Application Default Credentials use the `cloud-platform` scope. If access is missing, use `gcloud auth application-default login` or a local service account file set through `GOOGLE_APPLICATION_CREDENTIALS`. Keep settings, credential files, tokens and keys out of chat.
2. Confirm the target project and any quota project. Run one small read the user can recognize, such as `qwayk-gcp-safe-agent-cli compute instances-list --input-json input.json`. `inventory summary` reads the packaged inventory offline.
3. Explain what the read found before you suggest a change. Stop if the target is unclear, IAM blocks the request or the target is outside the configured project, folder, organization, billing account or region lists.
4. For a change, use `--bind-adc --plan-out plan.json` to prepare a plan for approval. Show the exact change, Google identity, quota project, risks, any likely cost and how you’ll check the result. Wait for the user.
5. After approval, use the same `--input-json` with `--plan-in plan.json --apply --yes`. Add `--ack-no-snapshot`, `--ack-irreversible` or `--ack-spend-money` only when required and covered by the approval. If anything changed, prepare a new plan.
6. Report what the receipt confirms. If a request is pending or the reply was lost, check the operation or resource before retrying. A successful reply alone is limited verification. Verify the resource with a read when you can.

Use the generated commands only. Refuse requests for arbitrary Google URLs or a permission bypass. Promise recovery only when the exact operation supports it and the user has reviewed the recovery plan. The saved test results cover installs and simulated Google replies. A real account read is still needed for live verification.
