# SEO plugins: what we can automate via API (no custom plugin)

This note documents what we learned about **setting per-post SEO fields** (SEO title, meta description, canonical URL, robots, social metadata) via HTTP API on **typical client WordPress sites**, with these constraints:

- Auth: WordPress **Application Passwords** (Basic Auth) for a normal user.
- Role: **Author** (can edit *their own* posts).
- No extra server work: **no custom helper plugin/snippet**, no PHP code changes.
- Target API: WordPress REST API (`/wp-json/wp/v2/...`) and any **SEO plugin-provided** REST API routes.

## Bottom line (simple)

- **Most SEO plugins are read-only from the API**: they expose *rendered* head output for headless frontends, but do not expose a stable way to *write* per-post SEO fields over REST without additional server-side enablement.
- **SEOPress** is the only major plugin we found with **documented write endpoints** that work with `edit_post` capability (so Authors can update SEO for their own posts) without extra custom integration.
- **AIOSEO** can be workable on some sites, but often depends on Pro features and/or admin capability mapping, so it’s not “zero-config across clients”.
- **Yoast** and **Rank Math** are generally **not writable** under these constraints.

## Plugin-by-plugin summary

### SEOPress (recommended)

- **Write support**: Yes, via dedicated REST endpoints.
- **Author support**: Yes, if the Author can `edit_post` for that post (their own posts).
- **Why it works**: the API checks `edit_post` (content permission), not admin-only capabilities.
- **Endpoint shape (examples)**:
  - `PUT /wp-json/seopress/v1/posts/{id}/title-description-metas`
  - `PUT /wp-json/seopress/v1/posts/{id}/meta-robot-settings`
  - `PUT /wp-json/seopress/v1/posts/{id}/social-settings`
- **Payloads**: structured JSON like `{"title": "...", "description": "..."}` (not raw meta keys).

Practical implication: If we want reliable SEO-field automation on client sites without custom code, we should prefer/target sites already using SEOPress (or recommend switching).

### All in One SEO (AIOSEO) (conditional)

- **Write support**: Sometimes.
- **Why “sometimes”**:
  - Some write behavior is tied to a REST API addon / Pro-tier features.
  - Sites may require admin configuration for role/capability access control before Authors can write SEO settings.
- **Integration style**: often via a special request key (example pattern: `aioseo_meta_data`) rather than plain `meta` keys.

Practical implication: treat as “maybe”. We can probe support per site and only use it if it actually works.

### Yoast SEO (not workable without extra enablement)

- **Write support**: effectively no, by default.
- **Why**:
  - SEO values live in “protected” meta keys like `_yoast_wpseo_*` that are not exposed as writable fields in the WP REST API by default.
  - Newer Yoast versions use **Indexables** (custom tables) and internal sync logic; direct meta writes are not a stable public integration contract.
- **What you can read**: headless output like `yoast_head_json` (rendered/calculated output, not a writable data contract).

Practical implication: we can publish content via API, but SEO fields usually must be set manually (unless the site already installed some “SEO fields via API” integration).

### Rank Math (not reliably workable without extra enablement)

- **Write support**: not reliably, by default.
- **Why**:
  - Even though Rank Math’s meta keys often don’t start with `_` (e.g. `rank_math_title`), they are typically **not registered as writable** in the WP REST schema, so updates may be ignored/stripped.
  - Rank Math’s “headless” feature (`getHead`) is read-only (returns rendered head HTML).
- **What you can read**: headless output and/or rendered head info, not a stable write API.

Practical implication: assume “cannot set SEO fields via API” on typical client sites.

### Slim SEO / The SEO Framework (not recommended for automation)

- Some plugins store settings in serialized arrays or intentionally minimize per-post overrides.
- Even if technically writable in some setups, it’s fragile (schema changes, race conditions, unclear contracts).

## What we can reliably do via WordPress REST as an Author (even without SEO plugin support)

- Create/update posts: title, content (blocks/HTML), excerpt, status (depending on permissions).
- Set featured image (if we can upload/select media).
- Set categories/tags.
- Basic post fields and formatting.

But per-post **SEO plugin fields** are plugin-specific; writing them requires either:
- the plugin exposes write endpoints (SEOPress), or
- the site has been configured to expose plugin meta fields in REST (not assumed), or
- admin-only credentials / custom code (out of scope for our constraint).

## Capability probe (next step)

We can add a small “capability probe” that:

1) Detects which SEO plugin is likely present (by checking read-only fields/endpoints).
2) Checks whether the plugin has a writable endpoint and whether the current credentials can use it.

Important: We should probe in a **non-destructive** way (no content changes) and produce a clear result like:

- `seo_plugin=seopress; can_write=true; endpoints=[...]`
- `seo_plugin=yoast; can_write=false; reason="no writable endpoints exposed"`

This doc is the baseline reference for that probe.

See also: `docs/seo_plugins/capability_probe.md` and
`docs/seo_plugins/capability_probe.py`.
