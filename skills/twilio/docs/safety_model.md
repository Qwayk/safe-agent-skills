# What happens before Twilio changes

The agent can run ordinary account reads by itself. Anything that can change the account, create cost, contact a person, or start bulk work stops at a plan first.

## Reads

Normal output hides credentials and fields that the pinned Twilio specifications mark as private. Use `--sensitive-out FILE` when sensitive provider output or a command-required snapshot must be saved in a local mode-`600` file. Some commands deliberately save a reduced privacy-safe snapshot rather than the complete response.

Only ordinary non-effectful `GET` requests may retry after a temporary Twilio error. Paid `GET` requests, such as Lookups, are plan-first and are not treated as ordinary reads.

## Plan first

Run an effectful command without `--apply` to create a dry-run plan:

```bash
qwayk-twilio-safe-agent-cli api-v2010 create-message \
  --input-json examples/inputs/create-message-plan.json \
  --plan-out .state/create-message.plan.json
```

Before returning that plan, the tool builds and validates the fixed request. Unknown fields, missing required values, wrong types, and unsupported bodies are refused before the user sees a plan. A plan therefore never makes an invalid input look review-ready.

Some operations have one documented field that contains JSON, such as Studio `Parameters` or Sync `Data`. The tool accepts flexible data only inside that exact field. Stringified form JSON is parsed, checked for the required object or array shape and size, and recursively redacted before it appears in a plan or receipt. Studio Flow definitions accept only widgets with complete current published child schemas and enforce their named property fields; nested actions and targets still add contact, spend, and bulk risk to the plan. Undocumented optional branches remain refused.

The plan is bound to the command, account fingerprint, exact input, pinned catalog, tool version, and any supplied snapshot. If one of those changes, apply is refused and a new plan is required.

The plan also names its risks, expected effect, verification method, snapshot rule, and required acknowledgements. Its target preview hides private data.

## Apply a reviewed plan

Applying the example message plan would require all of these flags:

```bash
qwayk-twilio-safe-agent-cli api-v2010 create-message \
  --input-json examples/inputs/create-message-plan.json \
  --plan-in .state/create-message.plan.json \
  --apply --yes \
  --ack-contact --ack-spend --ack-no-snapshot \
  --receipt-out .state/create-message.receipt.json
```

Do not run that command unless the sender, recipient, content, consent, and cost are all approved. `--apply --yes`, a mode-`600` reviewed plan, and a new `--receipt-out` path are always required. The tool creates the protected receipt before HTTP and refuses if the file cannot be created or already exists. The plan may also require one or more of:

- `--ack-contact`
- `--ack-spend`
- `--ack-bulk`
- `--ack-destructive`
- `--ack-auth`
- `--ack-identity`
- `--ack-production`
- `--ack-preview`
- `--ack-no-snapshot`

For a change with a useful before-state, supply `--snapshot-in FILE`. That file must already be mode `600`, and its hash becomes part of the plan. If no useful snapshot is available, most commands explain that limit and require `--ack-no-snapshot`.

SCIM user PATCH and Porting webhook configuration are stricter: both require the paired GET snapshot before a plan can be created. That snapshot carries the paired read command, account fingerprint, and an exact read-input hash; a mode-`600` file from another command, account, or target is refused. SCIM stores only the current `meta.version` plus a redaction marker in its protected snapshot, requires the request `If-Match` to equal that version, and refuses stale or missing lock input. Porting keeps its full before-state only in the protected snapshot, while normal output hides the configuration. Its target fields must be absolute HTTPS URLs on syntactically valid public hosts. Porting plans say plainly that POST overwrites the existing configuration. Neither command permits a no-snapshot acknowledgement.

## One attempt, then check

A write makes one Twilio request. It is never retried automatically, because repeating a send, call, purchase, Verify attempt, delete, or other real-world action can duplicate the effect.

Before that request, the tool creates a mode-`600` receipt with an `uncertain` preflight state. It then replaces the contents of that same protected file with the observed attempt result:

- `succeeded`: Twilio returned a 2xx response
- `failed`: Twilio returned a non-2xx response
- `uncertain`: no provider response arrived, so Twilio state must be checked before any retry

After a successful response, the tool re-fetches the resource when an exact paired read exists. Otherwise, it records the provider response as the available check. The receipt keeps the plan ID, command, HTTP status, provider status, snapshot receipt, post-write check, and a private-data-safe response.

`succeeded` means the HTTP attempt received a successful response. It does not mean a message was delivered, a call completed, or the requested business result was achieved.

`accepted`, `queued`, `scheduled`, `sending`, `sent`, and `completed` do not become `delivered`. Only a provider status of `delivered` or `read` is reported as delivery.

## Bulk means a named Twilio command

The tool has no CSV loop or generic jobs runner. A bulk action must be one of the fixed bulk commands in the catalog. Its plan derives the exact target list and count from the validated request body. A missing list, a declared count that does not match the list, or more than 25 targets is refused.

Apply requires `--ack-bulk` and `--target-count N`, where `N` exactly matches the derived count and is from 1 to 25. A normal send command refuses a list of recipients instead of quietly turning one request into a campaign.

The same cap applies when Twilio itself documents a larger provider limit. For example, Bulk Hosted Number Eligibility supports more numbers upstream, but this tool accepts at most 25 in one reviewed plan.

## No automatic undo

Some Twilio changes can be re-created or changed again; others cannot be restored. The tool does not promise rollback, backup, restore, or undo. If a live result is wrong, stop and review the receipt before preparing another change.

## Policy and private communications

The approval flags do not decide whether a message, call, recording, verification, or identity workflow is allowed. The account owner must confirm consent, Twilio policy, geographic permissions, recording rules, and any local legal requirements before apply. Twilio's current policy and security sources are linked in [official references](references.md).

Normal output hides communications content, identities, phone numbers, email addresses, transcripts, recording and media URLs, and non-JSON provider text. The SCIM and Porting command families also replace provider error details with a redaction marker so names, emails, and webhook URLs cannot escape through an error or failed-write receipt. Use a protected sensitive-output file only when the work genuinely needs that data. Recording media itself is outside this JSON CLI and must remain behind Twilio authentication and the account's recording security settings.

Webhook receiver hosting is outside this tool. If another service receives Twilio callbacks, it must validate the `X-Twilio-Signature` against the exact public URL and request parameters using Twilio's current validation guidance before trusting the event.
