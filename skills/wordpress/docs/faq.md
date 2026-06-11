# FAQ

**Why dry-run by default?** To prevent accidental edits.

**Why two caption commands?** WordPress stores captions both in media metadata and inside post content.

**Why does the tool refuse sometimes?** Because it can’t be sure it’s editing the right thing. Refusing is safer than making the wrong edit.

**Why use the REST API (not WP-CLI)?** This tool is designed to run remotely (no SSH) and to be reusable long-term, even if hosting changes.
