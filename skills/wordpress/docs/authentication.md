# Authentication

WordPress authentication is meant to be local and checked before an agent works with posts, pages, media, users, comments, settings, and plugin-related checks. Keep credentials local, run the safe check first, and do not paste secrets into chat.

The goal is simple: prove the tool can reach the right account without exposing private values or making a live change.

A good first auth check is: "Check the WordPress credential setup, run the safe auth check, and stop before any account change."

## Authentication notes

It calls `/wp-json/wp/v2/users/me` for a smoke test.

## Create an Application Password (recommended)

1. Log into WordPress admin.
2. Go to **Users → Profile** (or **Users → Your Profile**).
3. Find **Application Passwords**.
4. Create a new password (give it a name like `wordpress-api-tool`).
5. Copy it into `WP_APP_PASSWORD` (spaces are OK; the tool removes them).

## Common hosting gotcha: Authorization header is stripped

Some hosts/proxies block the `Authorization` header, which breaks Basic Auth.

If `auth check` returns 401/403 even with correct credentials, see `troubleshooting.md` for typical server fixes.
