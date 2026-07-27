# Engineering notes

## 2026-07-27 — Generated fixed inventory

The pinned official YAML contains 175 paths, 249 operations, and 49 tagged families. Every operation has an operation ID. Generation produces 248 unique commands and one intentional exclusion for `POST /batch`.

The official source hash is checked before generation, and `--check` compares all generated files byte for byte.

## 2026-07-27 — One shared executor without a request bridge

The CLI chooses only from packaged command names. The shared executor reads the already-fixed method and path from inventory; users cannot supply either. Parameters are limited to the operation's documented names and request bodies are limited to Asana's documented top-level envelope.

## 2026-07-27 — Write proof limits

PUT and DELETE operations use a same-path GET for before-state and readback when the spec provides one. Creates, actions, uploads, exports, and other operations without a reliable same-target GET require explicit no-snapshot acknowledgement and keep verification unproved. A captured before-state is never described as rollback.

## 2026-07-27 — Authenticated plans and fixed-request reconstruction

Schema-2 plans use HMAC-SHA256 with a random 32-byte key stored at `.state/plan-signing.key`. The signature covers the complete saved plan, including the public plan ID, but the key stays outside it. Apply verifies that signature before snapshot or provider work. It then reloads the chosen operation from the packaged fixed inventory, reconstructs the path and documented typed query from preserved inputs, and revalidates body, secret rules, file fields and hashes, risk, snapshot identity, verification, and rollback before using reconstructed values.

Unsigned and schema-1 plans are deliberately incompatible. A missing or changed key requires a new plan. This prevents recomputing a public plan ID from turning a fixed command into `/batch`, SCIM, another method, or another operation.

## 2026-07-27 — Private atomic local state

JSON plans and receipts use same-directory temporary files, file sync, and atomic replacement. The signing key is written completely to a private temporary file and linked into place only if no key already exists. Audit rows use atomic append-by-replacement. New files use `0600`, new directories use `0700`, and replacement removes group or world permissions without widening stricter existing owner permissions.

## 2026-07-27 — No live provider test

No credential or Asana request was authorized. HTTP, pagination, auth output, plans, drift, approvals, attachment metadata, receipts, failures, and async state handling are tested with injected clients. Live permissions, plans, scopes, rate limits, webhooks, files, exports, jobs, and provider response details remain unverified.
