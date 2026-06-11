# Safety model

This tool treats Freepik licensed downloads as **state-changing** operations because they may:
- create an account download record
- attach a license record to your account

Therefore:
- `download` is **dry-run by default**.
- Current `download --apply` requires explicit no-snapshot approval before the Freepik download/license endpoint, binary fetch, destination file write, or inventory row write until real saved snapshot support is available.
- `jobs run` requires **both** `--apply` and `--yes`, then inherits the same explicit no-snapshot approval on licensed download rows.

Remote write recovery:
- End state: `irreversible_and_clearly_labeled`
- Strategy: `no_inverse`
- Rollback readiness: `false`
- Backups: `[]`
- Snapshots: `[]`
- Rollback plan: `null`
- Restore note: licensed downloads and license records cannot be rolled back by this CLI; local cleanup is manual.

Current before-state rule:
- write plans include `before_state.required=true`, `before_state.supported=false`, and `before_state.status=no_snapshot_available`.
- fully gated licensed download applies require explicit no-snapshot approval before the provider write.
- no successful write receipt, destination file, or inventory row is emitted while before-state support is missing.

Additional guardrails:
- Migration non‑AI rule: `download` refuses unless the resource detail explicitly includes `is_ai_generated=false` AND `has_prompt=false` (missing/unknown flags are rejected).
- If `(resource_id, format)` already exists in the inventory, the tool refuses unless `--force` is provided.
- If the destination path already exists on disk, the future enabled apply path refuses unless `--force` is provided.
- When licensed download apply is safely enabled later, the tool writes `sha256` for the saved file.

Local helper writes are separate and are manual:
- `search/resource` with `--write-jobs` writes a local jobs CSV only.
- `preview --save-preview` writes preview files locally only.
- These local helper outputs can be deleted manually if you no longer need them.
