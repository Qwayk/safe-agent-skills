# Safety model

Rules:
- Dry-run by default; no writes unless `--apply`.
- Destructive actions need explicit irreversible acknowledgement.
- Writes without saved before-state, including `event send` and `site shared-links ensure`, need explicit no-snapshot approval.
- Verify after write when possible (Plausible Events API does not offer a reliable read-back).
- Refuse when unsure; do not guess.
- Refuse sending likely PII in event props (e.g. emails/tokens).
- Never log secrets.

## Recovery contract

Write plans now include `plan.recovery`.
Apply receipts now include `receipt.recovery`.

This tool currently uses two honest write end states:

- `irreversible_and_clearly_labeled`
- `rollback_by_inverse_action`

Current write-family map:

- `event send` -> `irreversible_and_clearly_labeled`
- `site create`, `site update`, `site delete`, `site shared-links ensure`, and `site goals delete` -> `irreversible_and_clearly_labeled`
- `site goals ensure`, `site custom-props ensure`, `site custom-props delete`, and `site guests ensure` -> `rollback_by_inverse_action`
- `site guests delete` -> `rollback_by_inverse_action` when current role is known, otherwise `irreversible_and_clearly_labeled`

Important detail:
- Before-state capture is written to `.state/plausible` under the directory containing `--env-file`.
- This CLI can persist before-state for:
  - `site create`, `site update`, `site delete`
  - `site goals ensure`, `site goals delete`
  - `site custom-props ensure`, `site custom-props delete`
  - `site guests ensure`
  - `site guests delete` when role is included in the guest list response
- This CLI cannot persist before-state for:
  - `event send` (no API read for exact state)
  - `site shared-links ensure` (no API path to fetch prior state)

## Events API verification note

Plausible's Events API does not provide a direct “read back this exact event” endpoint.
This tool supports a **best-effort** verification mode (`event send --verify`) after a successful apply.
It works best when you send to a unique, never-used URL path on the default domain.
