# Engineering decisions

## 2026-07-18: one generated boundary

The official source is `twilio/twilio-oai` at commit `1a9189c79a73781ddf45afcd0afd1f210742d68c`. The packaged catalog and the human coverage ledger are generated together. This avoids a CLI list that quietly differs from its documentation.

Command names are deterministic: `<spec-id>.<operation-id-kebab>`. The public CLI presents the same identity as `<spec-id> <operation-id-kebab>`.

## 2026-07-19: end-of-life and duplicate rows do not become commands

Programmable Chat, IP Messaging, and Notify operations whose product surface has passed Twilio's published end-of-life date are kept in coverage as `legacy_eol`, not exposed as callable commands. Notify's published EOL date was December 31, 2025.

Nine exact older routes point to their canonical current command: seven older Studio or Pricing routes and two deprecated Preview Marketplace writes superseded by stable Marketplace v1. Older operations with a different contract remain distinct commands rather than being merged by similar names.

Frontline is different because its retirement date is still in the future. Its two operations remain commands for existing customers, but the product has been end-of-sale since February 9, 2023 and is scheduled to retire on September 30, 2026. Treat them as access-gated and live-unverified. Regenerate and review the boundary before the retirement date so those commands do not remain callable after the official surface closes.

## 2026-07-19: audit incomplete request typing, then fail closed

Referenced request schemas are resolved into the packaged catalog. The executor validates required, unknown, read-only, enum, object, array, and primitive fields before a request. If a body schema does not expose safe fields, a non-empty body is refused.

The pinned OpenAPI left 81 writes empty or partly untyped. Each row was checked against current official Twilio documentation and Twilio-owned product schemas at Node repository commit `e9e546985dcc293e4f71888160725739e7b28c37`. This added 67 operation-specific commands. Two deprecated Preview Marketplace routes now point to the stable v1 commands. Twelve stay non-callable: the removed Studio v1 Engagement, five developer-preview operations without stable complete contracts, and six operations whose complete current contract is not public.

The SCIM reference now documents the PatchOp fields on a newer GA route, while the pinned operation boundary still contains the older preview organization route. The command deliberately keeps that pinned route, uses only the documented scalar subset, and remains preview, access-gated, and live-unverified. Porting webhook configuration is Public Beta and behaves as an overwrite even though the pinned operation is named `Create`; it therefore uses fetch-before-change and requires the paired snapshot.

The manual layer narrows provider contracts when the general tool guardrail is stricter. Studio Flow definitions use a fixed 20-widget safe subset whose child-property contracts are completely published, plus a fixed state envelope; the other current widget types stay refused. Video rules enforce filter exclusivity and uniqueness, and Bulk Hosted Number Eligibility is capped at 25 targets even though Twilio documents a larger upstream batch. Effectful paid reads require their risk acknowledgement but no snapshot acknowledgement because they do not change provider state.

Manual request supplements narrow only operations already present in the pinned boundary. Flexible JSON is accepted only in an exact documented field, with a declared object or array shape and size. Stringified form JSON is parsed before validation and recursively redacted. Known nested fields remain typed, and undocumented optional branches are refused. The official Node schemas are supporting evidence; they do not replace the pinned OpenAPI as the operation boundary.

## 2026-07-18: real-world effects are never retried

Only ordinary reads may retry temporary `429` or selected `5xx` responses. A paid read, send, call, purchase, Verify attempt, delete, or other effectful operation makes one provider attempt after plan approval.

The fixed request is validated before dry-run planning. For apply, a new protected receipt is created before HTTP; an existing or unwritable path stops the request. The receipt records `succeeded` for provider 2xx, `failed` for provider non-2xx, and `uncertain` when there was no response. That attempt state remains separate from provider delivery or completion status.
