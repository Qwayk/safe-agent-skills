---
name: cloudflare-api-safe-cli
description: Check Cloudflare accounts, DNS, Workers, Pages, access and logs. Show a plan and get approval before making Cloudflare changes.
---

# Cloudflare CLI

Use the `cloudflare-api-tool` command to inspect the account, explain what you found and prepare approved changes. Start with the named commands for the job. If a named command does not fit, use `operations list` and the [command guide](docs/command_reference.md) to find a supported operation. Use the documented CLI for provider requests.

## Find the right account and resource

1. Pass the intended `--env-file` on every command when the project has its own file. The file must exist. Its Cloudflare settings take precedence over the shell.
2. Run `auth check` and confirm `ok=true`. For a `cfat_` account token, or an unprefixed token identified by `CLOUDFLARE_ACCOUNT_ID`, the check uses `accounts list`. Confirm `verification=accounts_list` and, when the file sets an account ID, `configured_account_match=true`. For a user token, confirm the status is `active`.
3. List the accounts or zones needed for the job. Use the intended account, zone or Worker explicitly. Ask if more than one target could fit. Change the saved default with `accounts set-default` only with permission.
4. Use `auth probe --account-id <ACCOUNT_ID>` when you need to check product access. Use `auth doctor` to investigate slow requests. Both skip the user-token check for account-owned tokens. Run `auth zone-create-check` before planning bulk domain onboarding.

See the [setup and troubleshooting guide](docs/onboarding.md) for the env file and token settings. Keep credentials in the selected file and out of the reply.

## Read, plan and verify

- Run ordinary reads needed for the task. Save private results under `--project-dir` with `--apply --out <FILE>`. Examples include Worker code, KV values, snippet content, member details, Email Routing results and stored logs. Summarize the result and give the path. Keep log events, email addresses, secrets and raw private file contents out of the reply.
- For Worker tail streaming, keep the secret WebSocket URL in memory and write the events to the approved file. Use the [Worker tail command](docs/command_reference.md#workers-platform-inventory--safe-writes--sensitive-reads) and its flags.
- Prefer `browser-run` for page text, links, screenshots and crawling. These requests and read-like POSTs such as KV bulk get and Queue pull use `--apply --out`. Browser Run works with those flags alone.
- Before a Cloudflare write, show the plan and ask for approval of the exact target and change. Writes require `--apply --yes`. If there is no saved copy of the old settings, explain the recovery limit and get explicit approval before using `--ack-no-snapshot`. Use `--ack-irreversible` where the command requires it. Applied `operations` writes under `/accounts` must use redacted file output. Deletes there also need the extra acknowledgement.
- Check the result after a write. Report what changed, what the tool could confirm and where it saved the receipt. Check the current resource before retrying an unclear result. Read the [approval guide](docs/safety_model.md) before applying changes.

## First commands

```bash
cloudflare-api-tool --env-file "<ENV_FILE>" --output json auth check
cloudflare-api-tool --env-file "<ENV_FILE>" --output json accounts list
cloudflare-api-tool --env-file "<ENV_FILE>" --output json zones resolve --name "<ZONE_NAME>"
```
