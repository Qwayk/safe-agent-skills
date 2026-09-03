# Command reference

## Command shape

Every provider operation uses this fixed shape:

```bash
qwayk-twilio-safe-agent-cli <spec-id> <operation-kebab> --input-json INPUT.json
```

For example:

```bash
qwayk-twilio-safe-agent-cli api-v2010 fetch-account \
  --input-json examples/inputs/fetch-account.json
```

There is no command that accepts an arbitrary URL, HTTP method, or undeclared header. Use `qwayk-twilio-safe-agent-cli <spec-id> --help` to see the fixed operations under one specification.

Before writing an input file, inspect one command's exact safe contract:

```bash
qwayk-twilio-safe-agent-cli inventory show \
  --command api-v2010.create-message
```

This local command needs no credentials and makes no Twilio request. It reports the fixed method and path, declared path/query/header fields, allowed body fields and media types, required fields, auth schemes, risks, snapshot rule, and post-operation check. Use it instead of guessing field names from another command or reaching for a raw request.

## Utility commands

```bash
qwayk-twilio-safe-agent-cli --version
qwayk-twilio-safe-agent-cli inventory summary
qwayk-twilio-safe-agent-cli inventory show --command api-v2010.create-message
qwayk-twilio-safe-agent-cli onboarding
qwayk-twilio-safe-agent-cli onboarding --write-env
qwayk-twilio-safe-agent-cli auth check
qwayk-twilio-safe-agent-cli auth check --live
```

`onboarding` reports the needed settings. `--write-env` creates the selected env file at mode `600` and refuses to overwrite an existing file. `auth check` validates local credentials without a network request; `auth check --live` fetches the configured account.

## Credential-free local contracts

These fixed commands bypass provider configuration and make no network request:

```bash
qwayk-twilio-safe-agent-cli twiml conversation-relay-generate --input-json examples/inputs/conversation-relay-generate.json
qwayk-twilio-safe-agent-cli twiml conversation-relay-validate --input-json examples/inputs/conversation-relay-validate.json
qwayk-twilio-safe-agent-cli websocket conversation-relay-message-validate --input-json examples/inputs/conversation-relay-message.json
qwayk-twilio-safe-agent-cli webhook twilio-signature-validate --input-json examples/inputs/twilio-signature-validate.json
qwayk-twilio-safe-agent-cli agent-connect contract
```

ConversationRelay generation and validation accept only the strict `Response/Connect/ConversationRelay` shape and an absolute `wss://` URL. `Connect` supports only bounded relative-path or absolute HTTP(S) `action` references and `GET`/`POST` `method` values; nested `Language` children and `Parameter` children have independent cardinality and field limits. WebSocket validation accepts only the documented inbound and outbound message types. Signature validation reads the Auth Token from the environment variable named in `auth_token_env`; form parameters accept bounded scalar or repeated scalar values and use sorted unique Twilio canonicalization, while JSON requests hash the raw body and require the matching `bodySHA256` URL query value. Agent Connect output is local SDK/middleware metadata only.

## Global options

Global options go before the command group:

```text
--env-file FILE       Read settings from FILE instead of .env
--output json|text    Compact JSON by default; readable JSON in text mode
--verbose             Print only HTTP method, Twilio host, and status to stderr
--debug               Print a local Python traceback for tool errors
--version             Print one JSON version object
```

Example:

```bash
qwayk-twilio-safe-agent-cli --env-file .env.us1 --output json \
  api-v2010 fetch-account --input-json examples/inputs/fetch-account.json
```

## Input JSON

An input file may contain only these top-level sections:

```json
{
  "path": {},
  "query": {},
  "headers": {},
  "body": {},
  "content_type": "application/x-www-form-urlencoded"
}
```

Include only the sections the command needs. Parameter names and capitalization must match the pinned Twilio definition. Unknown sections, parameters, body fields, read-only fields, and media types are refused. The configured Account SID is filled automatically where the pinned command declares `AccountSid`; `fetch-account` also fills its account path value automatically.

## Read options

```text
--input-json FILE     Command-specific input object
--sensitive-out FILE  Save sensitive provider output or a required snapshot to a mode-600 file
```

Normal stdout stays private-data-safe. `--sensitive-out` does not make stdout unredacted; it creates a separate protected file and reports its hash and size.

## Plan and apply options

Effectful operations accept:

```text
--plan-out FILE       Save a dry-run plan at mode 600
--plan-in FILE        Load the prior reviewed plan for apply
--apply --yes         Confirm that the reviewed live operation may run
--snapshot-in FILE    Bind a protected current-state snapshot to the reviewed plan
--receipt-out FILE    Required for apply; save the result receipt at mode 600
--target-count N      Must equal the derived bulk target-list length; 1 through 25
```

The possible acknowledgement flags are:

```text
--ack-contact       --ack-spend        --ack-bulk
--ack-destructive   --ack-auth         --ack-identity
--ack-production    --ack-preview      --ack-no-snapshot
```

Use only the acknowledgements named in the generated plan. Extra flags do not replace a missing required one.
The tool validates the command input against the fixed contract before it produces a dry-run plan. A missing required field, unknown field, wrong type, unsupported content type, or unsafe body is refused before a plan exists.

The reviewed `--plan-in` file must still be mode `600`, and every live apply must name a new `--receipt-out` path before any provider request can run. Apply creates that mode-`600` receipt first. It refuses if the destination cannot be created or already exists, so an old receipt is never overwritten.

A bulk plan is created only when the validated request body contains the command's declared target list. The tool derives the count from that exact list and refuses a missing list, a conflicting `--target-count`, or more than 25 targets.

The pinned OpenAPI left some write fields untyped. Those operations were reviewed against current official Twilio docs and Twilio-owned product schemas. A command exists only when those sources support a fixed request contract. Rows without a stable complete contract stay non-callable under the exact disposition recorded in [API coverage](api_coverage.md).

Flexible JSON does not mean an arbitrary body. It is accepted only in the named field for that command. For example, `studio-v2.create-execution` may accept JSON in `Parameters`, Sync writes may accept JSON in `Data`, and Event Streams sink configuration must match one documented sink type. Stringified form JSON is parsed and checked for shape and size before planning. Unknown top-level fields, undocumented optional branches, and unsupported nested shapes are refused.

Two account-sensitive writes always require the paired snapshot. The protected snapshot records the paired GET command, account fingerprint, and hash of the exact read input. Planning refuses a snapshot from another command, account, or target even when the file has mode `600`. `iam-organizations.patch-organization-user` accepts only `replace`, eight documented scalar paths, and at most eight unique operations. A username change must include the primary-email leaf change with the same validated email, and `headers.If-Match` must equal the paired GET snapshot's `meta.version`. `numbers-v1.create-porting-webhook-configuration` is Public Beta; it accepts only the two HTTPS target fields on syntactically valid public hosts and the 12 notification values published in Twilio's POST request, and its POST overwrites the existing configuration. Neither command accepts `--ack-no-snapshot`.

The normal SCIM user GET output exposes only the resource version and a user redaction marker. The normal Porting configuration GET output hides the complete configuration. Their protected snapshots retain only the state needed for the reviewed write, and both command families replace provider error details with a redaction marker in normal errors and failed-write receipts.

## Receipt attempt states

The protected receipt exists before the HTTP request starts. Its `attempt.status` becomes:

- `succeeded` when Twilio returns a 2xx response
- `failed` when Twilio returns a non-2xx response
- `uncertain` when no provider response is received, including a timeout or connection exception

These states describe the provider attempt, not delivery. A succeeded message request can still be queued rather than delivered. If an attempt is uncertain, inspect Twilio state before considering another request.

## Paid Lookup example

A Lookup is plan-first because it can create cost:

```bash
qwayk-twilio-safe-agent-cli lookups-v2 fetch-phone-number \
  --input-json examples/inputs/lookup-phone-number.json \
  --plan-out .state/lookup.plan.json
```

After reviewing the plan, the paid request would be:

```bash
qwayk-twilio-safe-agent-cli lookups-v2 fetch-phone-number \
  --input-json examples/inputs/lookup-phone-number.json \
  --plan-in .state/lookup.plan.json \
  --apply --yes --ack-spend \
  --receipt-out .state/lookup.receipt.json
```

The examples are dry-run fixtures. No Lookup request was used as live proof.

## Output and refusals

JSON mode writes exactly one JSON object to stdout. Validation and provider errors use `ok: false`. A safety refusal uses `ok: true`, `refused: true`, and a reason, so an agent can treat the refusal as an expected safety result rather than retrying blindly.
