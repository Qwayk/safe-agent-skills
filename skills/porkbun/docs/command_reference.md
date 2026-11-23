# Command reference

The tool ships 66 named commands from the pinned Porkbun API spec. See the [coverage table](api_coverage.md) for paths and the [approval guide](safety_model.md) for writes.

## Global options

```bash
porkbun [--env-file <path>] [--output {json,text}] [--verbose] [--debug]
      [--timeout-s <seconds>]
      [--plan-out <plan.json>] [--plan-in <plan.json>]
      [--receipt-out <receipt.json>] [--secret-out <secret.json>]
      [--yes] [--ack-spend] [--ack-terms] [--ack-destructive]
      [--ack-secret] [--ack-send] [--ack-no-snapshot]
```

Use `--output json` to get one JSON object. Give `--input` the path to a JSON object file. For a write, run the command with `--plan-out` first. After approval, use `--plan-in`, `--yes` and the requested approval flags. Put `--apply` after the operation name.

## Account and onboarding

- `porkbun onboarding`
- `porkbun auth check`
- `porkbun operations list`

## Utility

- `porkbun utility get-ip`
- `porkbun utility ping-get`
- `porkbun utility ip-post [--input INPUT]`
- `porkbun utility ping [--input INPUT]`

## Pricing

- `porkbun pricing get-pricing-get`
- `porkbun pricing get-pricing [--input INPUT]`

## API key

- `porkbun api-key apikey-request [--input INPUT] [--apply]`
- `porkbun api-key apikey-retrieve [--input INPUT] [--apply]`

## Domain

- `porkbun domain get-domain --domain DOMAIN [--include-labels INCLUDE_LABELS]`
- `porkbun domain get-domain-glue --domain DOMAIN`
- `porkbun domain get-domain-ns --domain DOMAIN`
- `porkbun domain domain-get-registration-requirements --tld TLD`
- `porkbun domain get-transfer-get --domain DOMAIN`
- `porkbun domain get-domain-url-forwarding --domain DOMAIN`
- `porkbun domain get-domains [--api-access API_ACCESS] [--auto-renew AUTO_RENEW] [--domain DOMAIN] [--expiring-within-days EXPIRING_WITHIN_DAYS] [--include-labels INCLUDE_LABELS] [--name-contains NAME_CONTAINS] [--sort-direction SORT_DIRECTION] [--sort-name SORT_NAME] [--start START] [--tlds TLDS]`
- `porkbun domain list-domains [--input INPUT]`
- `porkbun domain list-transfers-get`
- `porkbun domain domain-add-url-forward --domain DOMAIN [--input INPUT] [--apply]`
- `porkbun domain domain-check-domain --domain DOMAIN [--input INPUT]`
- `porkbun domain domain-create --domain DOMAIN [--input INPUT] [--apply]`
- `porkbun domain domain-create-glue --domain DOMAIN --subdomain SUBDOMAIN [--input INPUT] [--apply]`
- `porkbun domain domain-delete-glue --domain DOMAIN --subdomain SUBDOMAIN [--input INPUT] [--apply]`
- `porkbun domain domain-delete-url-forward --domain DOMAIN --id ID [--input INPUT] [--apply]`
- `porkbun domain domain-get-glue --domain DOMAIN [--input INPUT]`
- `porkbun domain domain-get-ns --domain DOMAIN [--input INPUT]`
- `porkbun domain domain-get-url-forwarding --domain DOMAIN [--input INPUT]`
- `porkbun domain domain-renew --domain DOMAIN [--input INPUT] [--apply]`
- `porkbun domain transfer-domain --domain DOMAIN [--input INPUT] [--apply]`
- `porkbun domain domain-update-auto-renew [--domain DOMAIN] [--input INPUT] [--apply]`
- `porkbun domain domain-update-glue --domain DOMAIN --subdomain SUBDOMAIN [--input INPUT] [--apply]`
- `porkbun domain domain-update-ns --domain DOMAIN [--input INPUT] [--apply]`

## DNS

- `porkbun dns get-dnssec-records --domain DOMAIN`
- `porkbun dns get-dns-records --domain DOMAIN`
- `porkbun dns get-dns-record-by-id --domain DOMAIN --id ID`
- `porkbun dns get-dns-records-by-name-type --domain DOMAIN [--subdomain SUBDOMAIN] --type TYPE`
- `porkbun dns dns-create --domain DOMAIN [--input INPUT] [--apply]`
- `porkbun dns dns-create-dnssec-record --domain DOMAIN [--input INPUT] [--apply]`
- `porkbun dns dns-delete --domain DOMAIN --id ID [--input INPUT] [--apply]`
- `porkbun dns dns-delete-by-name-type --domain DOMAIN [--subdomain SUBDOMAIN] --type TYPE [--input INPUT] [--apply]`
- `porkbun dns dns-delete-dnssec-record --domain DOMAIN --keytag KEYTAG [--input INPUT] [--apply]`
- `porkbun dns dns-edit --domain DOMAIN --id ID [--input INPUT] [--apply]`
- `porkbun dns dns-edit-by-name-type --domain DOMAIN [--subdomain SUBDOMAIN] --type TYPE [--input INPUT] [--apply]`
- `porkbun dns dns-get-dnssec-records --domain DOMAIN [--input INPUT]`
- `porkbun dns dns-retrieve --domain DOMAIN [--input INPUT]`
- `porkbun dns dns-retrieve-by-id --domain DOMAIN --id ID [--input INPUT]`
- `porkbun dns dns-retrieve-by-name-type --domain DOMAIN [--subdomain SUBDOMAIN] --type TYPE [--input INPUT]`

`dns dns-edit` can change only the fields you supply. Use the record ID and include at least one DNS field in the input, such as `{"ttl": 900}`. To move a record to the root of the domain, pass `"name": ""`. `dns dns-edit-by-name-type` affects all matches for that name and type and still requires `content`.

## SSL

- `porkbun ssl get-ssl-retrieve --domain DOMAIN`
- `porkbun ssl ssl-retrieve --domain DOMAIN [--input INPUT]`

## Email hosting

- `porkbun email-hosting email-set-password [--input INPUT] [--apply]`

## Marketplace

- `porkbun marketplace list-marketplace-listings-get [--limit LIMIT] [--query QUERY] [--sld-length-max SLD_LENGTH_MAX] [--sld-length-min SLD_LENGTH_MIN] [--sort-direction SORT_DIRECTION] [--sort-name SORT_NAME] [--start START] [--tlds TLDS]`
- `porkbun marketplace list-marketplace-listings [--input INPUT]`

## Account

- `porkbun account get-api-settings`
- `porkbun account get-balance`
- `porkbun account get-account-invite-status [--input INPUT]`
- `porkbun account create-account-invite [--input INPUT] [--apply]`

For `get-account-invite-status`, `INPUT` must be a JSON file containing the token:

```json
{"token":"INVITE_TOKEN"}
```

Pass the private file with `--input`. The CLI rejects `--token` before calling Porkbun.

## Webhooks

- `porkbun webhooks webhook-deliveries [--endpoint-id ENDPOINT_ID] [--limit LIMIT] [--start START] [--status STATUS]`
- `porkbun webhooks webhook-delivery --id ID`
- `porkbun webhooks webhook-event-types`
- `porkbun webhooks webhook-get --id ID`
- `porkbun webhooks webhook-list`
- `porkbun webhooks webhook-create [--input INPUT] [--apply]`
- `porkbun webhooks webhook-delete [--input INPUT] [--apply]`
- `porkbun webhooks webhook-resend [--input INPUT] [--apply]`
- `porkbun webhooks webhook-rotate-secret [--input INPUT] [--apply]`
- `porkbun webhooks webhook-test [--input INPUT] [--apply]`
- `porkbun webhooks webhook-update [--input INPUT] [--apply]`

## Where to make source changes

- `src/qwayk_porkbun_safe_agent_cli/cli.py` handles commands, plans, requests and receipts. `config.py`, `http.py`, `privacy.py` and `secure_files.py` handle settings, transport, redaction and private files.
- `scripts/generate_inventory.py` and `scripts/porkbun_inventory_policy.json` generate the command map and coverage.
- `tests/test_cli.py` and `tests/test_http.py` check runtime behavior. `tests/test_api_inventory.py` checks command coverage and packaged data.

To change a named command, check its source in the pinned spec and update the relevant policy, runtime and tests. For writes, check the plan, approval flags, before-state handling and receipt with the same command a user would run. See [offline checks](proof.md).
