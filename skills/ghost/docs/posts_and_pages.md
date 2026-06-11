# Posts and pages

Ghost posts and pages are similar at the API level:
- posts: `/admin/posts/...`
- pages: `/admin/pages/...`

Key safety rule:
- updates require `updated_at`, so every write does GET → PUT → GET verify.

Tag/author relations are replaced (not merged), so the tool always GETs first and merges locally.

## HTML updates (`source=html`) and verification

When you update content with `source=html`, Ghost may normalize the stored HTML.

This tool verifies `--source html` updates using a best-effort normalization (entities, auto-added heading IDs, auto-added link attributes, internal absolute ↔ relative URLs, whitespace).
This avoids false “verification failed” errors when the semantic change is correct.

## Creating and deleting pages

The Admin API supports creating pages with `POST /admin/pages/` and deleting with `DELETE /admin/pages/{id}/`.

This tool exposes:
- `ghost-api-tool page create` (create from `html` or `lexical`)
- `ghost-api-tool page delete` (delete by slug or id)
- `ghost-api-tool page sync-md` (Markdown → HTML → Lexical via `source=html`)

Safety:
- All write commands are dry-run by default; add `--apply` to actually write.
- `page sync-md` can delete and recreate a page when `--replace-existing` is used; the dry-run output shows the exact actions first, and that replace-existing path now saves the old page state before apply.
- `page sync-md` stays dry-run-only when it would create a brand-new page, because there is no current page state to save first.

## Post body editing modes

Ghost stores editor content in Lexical, but some migration tasks are easier to do in HTML.

This tool supports two body-editing approaches:
- `post body ...` (HTML card mode): only works if the post contains a single HTML card.
- `post bodylex ...` (Lexical mode): operates directly on Lexical nodes (currently images-first).

## Tags and authors on posts

Ghost supports attaching tags and authors as part of a post payload:
- tags can be identified by **name** (and missing tags are auto-created)
- authors can be identified by **email** (or id)

This tool primarily manages tags/authors **via post updates** for reliability and simplicity.
