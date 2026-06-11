# Application Passwords

Last verified (UTC): 2026-01-27

Official docs:
- https://wordpress.org/documentation/article/application-passwords/

Notes:
- Application Passwords were introduced in WordPress 5.6.
- They authenticate over HTTP Basic Auth (username + application password).
- Some hosts/security plugins block or strip the `Authorization` header, which breaks REST auth.
- If auth fails unexpectedly:
  - confirm the site supports `/wp-json/`
  - confirm the Application Password exists and is not revoked
  - check for security plugins/host restrictions

