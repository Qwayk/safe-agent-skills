# Command reference

This tool exposes explicit Zapier commands only. It does not accept raw method/path input.

## Global flags

- `--version`
- `--output json|text`
- `--env-file <file>`
- `--timeout-s <seconds>`
- `--verbose`
- `--apply`
- `--plan-in <file>`
- `--plan-out <file>`
- `--receipt-out <file>`
- `--yes`
- `--ack-irreversible`
- `--ack-no-snapshot`

## Safety and help commands

- `qwayk-zapier-safe-agent-cli onboarding [--no-write-env]`
- `qwayk-zapier-safe-agent-cli auth check`
- `qwayk-zapier-safe-agent-cli runs list [--limit 20]`
- `qwayk-zapier-safe-agent-cli runs show --run-id <id>`

## Partner API

- `qwayk-zapier-safe-agent-cli partner apps-list`
- `qwayk-zapier-safe-agent-cli partner categories-list`
- `qwayk-zapier-safe-agent-cli partner profiles-me-list`
- `qwayk-zapier-safe-agent-cli partner zap-templates-list`
- `qwayk-zapier-safe-agent-cli partner zaps-list`
- `qwayk-zapier-safe-agent-cli partner create-action-run --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli partner retrieve-action-run --id <value>`
- `qwayk-zapier-safe-agent-cli partner get-actions --app <value>`
- `qwayk-zapier-safe-agent-cli partner get-fields-inputs --action-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli partner get-choices --action-id <value> --input-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli partner get-fields-outputs --action-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli partner test-action --action-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli partner get-v2-apps`
- `qwayk-zapier-safe-agent-cli partner get-authentications --app <value>`
- `qwayk-zapier-safe-agent-cli partner create-authentication --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli partner authorize-list --client-id <value> --redirect-uri <value> --response-type <value> --scope <value>`
- `qwayk-zapier-safe-agent-cli partner create-zap-guess --client-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli partner v2-whitelabel-apps-list`
- `qwayk-zapier-safe-agent-cli partner get-zap-runs`
- `qwayk-zapier-safe-agent-cli partner get-v2-zaps`
- `qwayk-zapier-safe-agent-cli partner post-zaps --body-json '<json>'`

## Trigger Inbox API

- `qwayk-zapier-safe-agent-cli trigger-inbox listTriggerInboxes`
- `qwayk-zapier-safe-agent-cli trigger-inbox createTriggerInbox --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli trigger-inbox ensureTriggerInbox --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli trigger-inbox deleteTriggerInbox --id <value>`
- `qwayk-zapier-safe-agent-cli trigger-inbox getTriggerInbox --id <value>`
- `qwayk-zapier-safe-agent-cli trigger-inbox patchTriggerInbox --id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli trigger-inbox pauseTriggerInbox --id <value>`
- `qwayk-zapier-safe-agent-cli trigger-inbox resumeTriggerInbox --id <value>`
- `qwayk-zapier-safe-agent-cli trigger-inbox getTriggerInboxEvents --inbox-id <value>`
- `qwayk-zapier-safe-agent-cli trigger-inbox listTriggerInboxMessages --inbox-id <value>`
- `qwayk-zapier-safe-agent-cli trigger-inbox acknowledgeTriggerInboxMessages --inbox-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli trigger-inbox leaseTriggerInboxMessages --inbox-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli trigger-inbox releaseTriggerInboxMessages --inbox-id <value> --body-json '<json>'`

## Promotions API

- `qwayk-zapier-safe-agent-cli promotions create --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli promotions destroy --enrollment-id <value>`
- `qwayk-zapier-safe-agent-cli promotions retrieve --enrollment-id <value>`

## AI Actions API

- `qwayk-zapier-safe-agent-cli ai-actions ai-actions-list-ai-actions`
- `qwayk-zapier-safe-agent-cli ai-actions ai-actions-create-ai-action --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions ai-actions-delete-ai-action --ai-action-id <value>`
- `qwayk-zapier-safe-agent-cli ai-actions ai-actions-get-ai-action --ai-action-id <value>`
- `qwayk-zapier-safe-agent-cli ai-actions ai-actions-update-ai-action --ai-action-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions ai-actions-execute-ai-action --ai-action-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions ai-actions-preview-ai-action --ai-action-id <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions search-search-apps`
- `qwayk-zapier-safe-agent-cli ai-actions actions-get-app-details --app <value>`
- `qwayk-zapier-safe-agent-cli ai-actions search-search-actions --app <value>`
- `qwayk-zapier-safe-agent-cli ai-actions actions-get-action-details --app <value> --action <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions actions-list-authentications-for-app --app <value>`
- `qwayk-zapier-safe-agent-cli ai-actions actions-get-prefill-choices --app <value> --prefill <value> --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions meta-get-account-list`
- `qwayk-zapier-safe-agent-cli ai-actions meta-check-user-auth`
- `qwayk-zapier-safe-agent-cli ai-actions meta-get-user-login-link --sign-up-first-name <value> --sign-up-last-name <value> --sign-up-email <value>`
- `qwayk-zapier-safe-agent-cli ai-actions meta-get-oauth-login-link --client-id <value> --redirect-uri <value> --code-challenge <value> --sign-up-email <value>`
- `qwayk-zapier-safe-agent-cli ai-actions execute-execute-stateless-action --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions execution-log-rate-execution-log --execution-log-id <value>`
- `qwayk-zapier-safe-agent-cli ai-actions guess-guess-actions --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions meta-app-health-check`
- `qwayk-zapier-safe-agent-cli ai-actions meta-shrink-result --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions unfurl-unfurl-url --body-json '<json>'`
- `qwayk-zapier-safe-agent-cli ai-actions unfurl-get-unfurl-apps`
- `qwayk-zapier-safe-agent-cli ai-actions unfurl-check-user-auth-for-app --app <value>`

## Write pattern

Run the write command without `--apply` first. Review the JSON plan. Then apply from that plan only when the target, request body, and risk are correct.

```bash
qwayk-zapier-safe-agent-cli --output json --plan-out plan.json partner post-zaps --body-json '<json>'
qwayk-zapier-safe-agent-cli --output json --apply --plan-in plan.json --ack-no-snapshot --receipt-out receipt.json partner post-zaps --body-json '<json>'
```
