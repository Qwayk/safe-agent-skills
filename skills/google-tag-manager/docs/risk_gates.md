# Risk gates (GTM API v2)

Purpose:
- Make “what requires which flags” explicit and reviewable.
- Keep the mapping deterministic so agents and humans can predict refusals.

This tool labels each method as one of:
- `low` (read)
- `medium` (single-resource writes)
- `high` (batch / conflict resolution / linking / large moves)
- `irreversible` (DELETE and publish-like operations; production impact)

Risk level and recovery are separate:
- `risk_level` says how risky the action is.
- `recovery.end_state` says whether the tool can emit a direct inverse action.

## Safety gates per risk level

- `low`
  - Allowed without `--apply`.
  - Retries enabled (see `GTM_READ_RETRIES`).

- `medium`
  - Dry-run plan by default.
  - Apply requires: `--apply`
  - `--plan-in` is optional (but recommended); if provided, drift detection is enforced.

- `high`
  - Dry-run plan by default.
  - Apply requires: `--apply --yes --plan-in`

- `irreversible`
  - Dry-run plan by default.
  - Apply requires: `--apply --yes --ack-irreversible --plan-in`

## GTM method mapping (rules)

Low:
- Any `GET` method
- `tagmanager.accounts.containers.workspaces.folders.entities` (read-like `POST`)

Irreversible:
- Any `DELETE` method
- Any method id containing `.publish` (publishes changes live)

High (method id contains any of):
- `.combine`
- `.bulk_update`
- `.resolve_conflict`
- `.sync`
- `.move_tag_id`
- `.move_entities_to_folder`
- `.destinations.link`
- `.import_from_gallery`
- `.revert`

## Apply gate for no safe pre-read family

- Families without a safe `GET` pre-read endpoint must disclose that no useful before-copy can be saved.
- Live apply for those families requires explicit no-snapshot approval and a clear recovery warning, and it still refuses when the target is unclear, permissions are missing, the action is unsupported, or a safety check fails.

Medium:
- Most other `POST` / `PUT` / `PATCH` methods
- `.quick_preview` is treated as `medium`

## Recovery mapping (first GTM pass)

`recovery.end_state` uses only these values for write methods:
- `rollback_by_inverse_action`
- `irreversible_and_clearly_labeled`

`rollback_by_inverse_action` is only used when the discovery methods show a direct inverse action without guessing:
- `create`, `update`, or `delete` in a family that also has `.revert`
- `delete` in a family that also has `.undelete`
- `create` in a family that also has `.delete`
  - for create, the rollback plan becomes concrete only after apply if the API response returns the created resource `path`

`irreversible_and_clearly_labeled` is used for every other write method, including:
- normal writes with no direct inverse action in discovery
- high-risk action methods like `.combine`, `.bulk_update`, `.resolve_conflict`, `.sync`, `.move_tag_id`, `.move_entities_to_folder`, `.destinations.link`, `.import_from_gallery`
- publish-like methods
