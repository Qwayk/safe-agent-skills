# Troubleshooting

## Auth check fails

- Confirm Application Password is correct.
- Confirm your user has permission to edit posts/media.
- Confirm your WordPress version supports Application Passwords (5.6+).
- Some security plugins disable Application Passwords or block REST requests.

### 401/403 but credentials are correct (Authorization header stripped)

On some hosts, the `Authorization` header is not passed through to PHP/WordPress.
This makes Basic Auth fail even with correct credentials.

Typical fixes (you only need one, depending on your stack):

- **Nginx + PHP-FPM**: ensure `HTTP_AUTHORIZATION` is forwarded:
  - `fastcgi_param HTTP_AUTHORIZATION $http_authorization;`
- **Apache**: ensure the header is available to PHP:
  - `RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]`

If you can’t change server config (managed hosting), use a host-supported auth method or a different environment.

## Missing `content.raw`

Some content commands request `context=edit` (example: `post get --include-raw`) so WordPress can return `content.raw`.
If your auth does not allow it, WordPress may omit `content.raw`.

Fix:
- Use a user that has permission to edit the post type.
- Confirm the REST API is not being filtered by a plugin.

## Post caption did not change

If the site uses non-Gutenberg structures, `post set-image-captions` will refuse. Use `media set` instead, or extend the content editor safely.

How to check:
- Run `wordpress-api-tool post get --slug SLUG --include-raw` and search for `<!-- wp:image`.

## `--apply` “doesn’t work”

`--apply` is a global flag, so it must come **before** the command:

- Correct: `wordpress-api-tool --apply media set --id 123 --caption "..."`  
- Incorrect: `wordpress-api-tool media set --id 123 --caption "..." --apply`

## Debug errors

By default the tool prints a single JSON error message.
If you want the full Python stack trace (developer debugging), add `--debug`.
