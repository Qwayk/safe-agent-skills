# Command reference

The shipped CLI maps Porkbun’s 53 documented API paths to 66 fixed provider commands: 39 reads and 27 writes. It does not accept arbitrary methods, paths, URLs, or raw requests.

## Global options

```bash
porkbun [--env-file <path>] [--output {json,text}] [--verbose] [--debug]
      [--timeout-s <seconds>]
      [--plan-out <plan.json>] [--plan-in <plan.json>]
      [--receipt-out <receipt.json>] [--secret-out <secret.json>]
      [--yes] [--ack-spend] [--ack-terms] [--ack-destructive]
      [--ack-secret] [--ack-send] [--ack-no-snapshot]
```

- Use `--output json` for structured output.
- `--plan-out`, `--plan-in`, `--receipt-out`, and `--secret-out` are used for review, apply, and audit flow.
- `--apply` is passed on a command, not globally.
- `--yes` is required for apply and stronger apply gates.

Write-capable commands always need an explicit review path first.

## Local files and request safety

- A saved plan is authenticated with HMAC-SHA256 using the local owner-only `.state/plan-signing.key`. Plan and apply must share that same local key and `.state`; apply refuses a changed plan, a missing key, or a different key.
- The first process to initialize the signing key wins without overwriting an existing key. Concurrent first-plan commands then read and use that same validated 32-byte `0600` key.
- Plans, receipts, secret results, and onboarding `.env` files are written atomically with `0600` permissions. Tool-created `.state`, `.state/plans`, and `.state/receipts` directories use `0700`. The signing key uses `0600`.
- Active plan, receipt, and secret output paths must be distinct from one another and from `--env-file`, `--input`, and `--plan-in`. This applies to default and explicit paths, including relative/absolute, `..`, symbolic-link, and existing-file aliases. A collision stops before a provider request or file replacement.
- A secret-bearing command requires `--ack-secret` and `--secret-out`. The CLI checks and reserves the destination before any provider call. An unsafe, invalid, or unwritable destination means no request is sent.
- Redirect following is disabled. Every HTTP `3xx` response fails and cannot produce a successful write receipt.
- `PORKBUN_API_HOST=default` selects `https://api.porkbun.com/api/json/v3`; `PORKBUN_API_HOST=ipv4` selects `https://api-ipv4.porkbun.com/api/json/v3`. No other production host is accepted.

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

The token is file-only. Never pass it with `--token`; the CLI rejects that form before any provider call.

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

## Read/write split

- The fixed 66-command surface contains 39 read commands and 27 write commands across 53 provider paths.
- The 27 writes are all in this explicit list:
  - `api-key apikey-request`, `api-key apikey-retrieve`
  - `domain domain-add-url-forward`, `domain domain-create`, `domain domain-create-glue`, `domain domain-delete-glue`, `domain domain-delete-url-forward`, `domain domain-renew`, `domain transfer-domain`, `domain domain-update-auto-renew`, `domain domain-update-glue`, `domain domain-update-ns`
  - `dns dns-create`, `dns dns-create-dnssec-record`, `dns dns-delete`, `dns dns-delete-by-name-type`, `dns dns-delete-dnssec-record`, `dns dns-edit`, `dns dns-edit-by-name-type`
  - `email-hosting email-set-password`
  - `account create-account-invite`
  - `webhooks webhook-create`, `webhooks webhook-delete`, `webhooks webhook-resend`, `webhooks webhook-rotate-secret`, `webhooks webhook-test`, `webhooks webhook-update`

Repository verification did not use a live Porkbun account and made no live provider calls. These checks prove the local command, validation, privacy, file-safety, redirect, and refusal behavior; they do not prove live-account responses.
