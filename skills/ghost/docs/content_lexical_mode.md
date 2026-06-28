# Content Lexical mode

Ghost stores post bodies in a Lexical JSON document (`post.lexical`).

This tool’s `post bodylex ...` commands operate on that Lexical document directly.

## Why this exists

- Most real posts are normal Ghost editor posts (Lexical), not single HTML cards.
- Editing Lexical is more powerful than HTML-card mode, but it must be done carefully to avoid corrupting content.

## Safety rules

- Dry-run by default; writes require `--apply`.
- Applying edits to a non-draft post is refused unless you pass `--allow-published` (or you gate edits with `--require-current draft`).
- Every write does GET → PUT → GET, then an idempotence verification (re-running the same transform must be a no-op).
- If selection is ambiguous (e.g. multiple matching headings), the command refuses and explains what extra selector is needed.
- If a post has no Lexical field, it may be using `mobiledoc` (older imports). In that case, use:
  - `ghost-api-tool post bodymob ...`

## What is supported today

Images-first, because it maps directly to common migration work:
- Inspect images and their current `src`, `alt`, `caption`, and context heading.
- Inspect output also includes `title` (if present) and the Lexical `path` for debugging.
- Scaffold a `replace-many` mapping for captions/alts (`post bodylex scaffold captions-map`) to reduce copy/paste.
  - Default: only images missing captions (`--mode missing`)
  - Migration workflow: rewrite **all** images (`--mode all --include-context`)
  - Cleanup workflow: only fix policy mismatches (`--mode nonconforming --include-context`)
- Replace a specific image `src` (exact match).
- Replace many image `src` values at once from a JSON mapping (`replace-many`).
- Replace the Nth image after a top-level heading (`root.children`) by heading text.
  - Optional safety: pass `--expect-old-src` to refuse if the targeted image is not what you expect.
- Update image `alt` / `caption` / `title` by `src`.
- Insert an image after a top-level heading by cloning a template image node (`--template-src`).
- Delete image nodes by exact `src` (`delete-by-src`) to remove duplicates safely.
- Remove all top-level images and re-insert specific images immediately before headings (`sync-before-headings`) for a single-pass cleanup + placement. For migration work, the `placements.json` should be authored manually (do not auto-generate captions).
- Fix common WordPress importer artifacts where list items are stored as HTML cards instead of native lists:
  - `post bodylex fix-numbered-list-after-heading` (split `<ol>` cards)
  - `post bodylex fix-bullet-lists-split-html-cards` (split `<ul>` cards)
  - `post bodylex convert-html-list-cards` (standalone `<ul>/<ol>` HTML list cards → native lists)

## Paid link compliance (Lexical links)

Some affiliate/paid link compliance requires `rel="noreferrer noopener sponsored nofollow"`.

This tool can enforce that on Lexical link nodes:
- Amazon-only: `ghost-api-tool post bodylex set-amazon-link-rel --slug SLUG --diff`
- Generic paid links:
  - Host mode: `ghost-api-tool post bodylex set-paid-link-rel --slug SLUG --host hellofresh.com --host sovrn.co --diff`
  - All external mode: `ghost-api-tool post bodylex set-paid-link-rel --slug SLUG --all-external --diff`

Important:
- Only touches Lexical `type="link"` nodes.
- Does not modify links inside HTML cards.
- Preserves existing rel tokens; only adds missing tokens.

## Notes about captions

Ghost image captions are stored as a string in the image node’s `caption` field and are commonly HTML-wrapped.
When you provide `--caption "plain text"`, the tool wraps it as:

`<span style="white-space: pre-wrap;">…</span>`

If you provide a caption that already contains HTML tags, it is used as-is.

## Caption policy

We use two explicit caption endings:
- Stock: `(stock image; for illustration only).`
- Original infographic: `(original infographic by the publisher).`

To audit whether a post matches the policy:
- `ghost-api-tool post audit --id ID --enforce-caption-policy`
