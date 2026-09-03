# Architecture

The tool has three parts: a pinned operation catalog, a fixed request executor, and Twilio-specific safety rules.

## Pinned catalog

`scripts/generate_twilio_inventory.py` reads 60 official JSON specifications from the pinned `twilio/twilio-oai` commit. It generates the packaged operation catalog and `docs/api_coverage.md` together, so command registration and the coverage ledger use the same rows.

The catalog records method, server, literal path, declared parameters, request schemas, auth requirements, private-data annotations, version relationships, risk labels, snapshot strategy, and post-write check strategy. The loader refuses a catalog whose disposition totals differ from the pinned boundary.

The pinned OpenAPI is still the operation boundary. For 81 writes whose pinned request typing was incomplete, the generator records a separate operation-specific decision supported by current official Twilio documentation and Twilio-owned product schemas. Sixty-seven rows receive fixed manual request supplements, two deprecated Preview routes map to stable Marketplace v1 commands, and 12 remain non-callable with exact evidence. A manual supplement can narrow an operation to documented fields; it cannot add a new route or widen the tool into a generic request path.

## Fixed request executor

The CLI registers one `<spec-id> <operation-kebab>` parser for each callable catalog row. The request builder accepts only declared path, query, header, body, and media-type input. It fills the configured Account SID where the operation expects it and refuses unknown input.

Some Twilio form fields contain JSON. The catalog marks only the exact documented field for that operation. The executor parses the string, checks its required object or array shape and size, validates known nested fields, and recursively redacts private values. The safety classifier also parses valid object or array strings so a nested Studio action cannot hide contact, spend, or bulk risk. Native flexible JSON follows the same named-field rule. Other untyped or undocumented branches are refused.

Authentication and regional routing are selected from the operation metadata. The HTTP layer sends requests only to the fixed Twilio server and path. There is no raw URL, arbitrary method, SDK pass-through, or generic request command.

## Safety policy

Ordinary reads run directly with private-data-safe output. Paid reads and writes create a plan bound to the exact command, account fingerprint, input hash, inventory hash, tool version, and optional snapshot hash. Commands that can replace an account-level configuration may require the snapshot rather than permit a no-snapshot acknowledgement. For required snapshots, the protected snapshot envelope also binds the paired GET command, account fingerprint, and compatible read-input hash; the runtime rejects a file from another command, account, or target. SCIM PATCH additionally requires the request `If-Match` to equal the paired GET's `meta.version`.

SCIM user and Porting webhook configuration reads use operation-specific privacy views. Normal SCIM output keeps only `meta.version`; normal Porting output hides the complete configuration. Protected snapshots retain the minimum state needed for planning, and provider error details are redacted for both command families, including failed Porting write receipts. Porting target URLs are accepted only when they use HTTPS and a syntactically valid public hostname or global IP address.

Effectful input is validated through the fixed request builder before dry-run planning. Apply then verifies the plan binding and acknowledgements and creates a new protected receipt before HTTP. An unwritable or existing destination stops the request. The one non-retried attempt updates the receipt to `succeeded` for a 2xx response, `failed` for a provider non-2xx response, or `uncertain` when no provider response arrives. A paired read runs after success when one exists. Provider statuses are preserved instead of treating acceptance as delivery.

The policy also refuses multi-recipient input on normal contact commands. Bulk actions exist only through named catalog operations. A plan must derive the exact target list and count from the validated body, and it refuses a missing list, count mismatch, or more than 25 targets.
