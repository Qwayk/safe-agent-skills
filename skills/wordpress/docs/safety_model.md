# Safety model

WordPress can touch posts, pages, media, users, comments, settings, and plugin-related checks, so the safe path is to look first, plan second, and change last. Reads and dry-run plans are where the agent should do most of its thinking. Real changes should only happen after the plan is reviewed and the required approval flags are present.

That matters because the risky part is usually not the command syntax. It is choosing the wrong account, changing the wrong live resource, exposing sensitive output, or approving a change that cannot be cleanly undone.

A good safety ask is: "Read the post, page, or site state first, then review the plan before publishing, deleting, media, user, or setting changes."

## Core safety rules

- Dry-run by default; no writes unless `--apply`.
- Verify after write: re-fetch and assert.
- Refuse when unsure: no guessing edits.
- Batch jobs require `--apply` and `--yes`, but write mode is currently blocked for safe-state reasons until per-row before-state restore is available.
- Audit logs never include secrets.
- Several write families now save old state first under `.state/runs/<run-id>/before/`.

Tip:
- `--apply` is a global flag, so use it like `wordpress-api-tool --apply <command> ...`.

## Intentional scope + least privilege

This tool is designed to be safe-by-default for **content workflows** (posts/pages/media), not full WordPress administration.

- Prefer a dedicated WordPress user (a “service account”) with the minimum role needed.
- Avoid using an Administrator account; reducing account permissions reduces blast radius if something goes wrong.
- The CLI intentionally does not expose commands for many high-risk administrative areas (plugins/themes, templates/global styles, site-wide settings writes, menus/navigation, etc.).

## What “refuse” means

If the tool can’t confidently target the right thing (for example, an image caption that isn’t inside a Gutenberg `wp:image` block where it can determine the attachment id), it will:
- do **nothing**
- return a clear message in the output explaining **why** it refused

This is intentional: “no change” is safer than “wrong change”.

## No automatic retries on writes

Reads may retry on transient errors; writes do not retry automatically to avoid duplicate/partial updates.

## Verification approach

- Media updates: the tool re-fetches the media item and compares the exact fields you set.
- Post-body edits: the tool re-fetches the post and checks that re-running the same edit would produce **zero** additional changes.
- Status changes: the tool re-fetches the post and asserts the returned `status` matches what you requested. Use `--require-current draft` as a guardrail.
- Exact replacements: `post replace-in-content` re-fetches the post and verifies the source string occurs the expected number of times after the replacement (`remaining_source_occurrences == expected_remaining_source_occurrences`).
- Before these applies, the upgraded write families save the current target state locally so the plan and receipt can point back to it.

## Batch jobs are extra strict

Batch edits require:
- `--apply` and `--yes` for command parsing, then are blocked in write mode in this release
