"""Auth lifecycle helpers are intentionally absent.

The CLI accepts an already-issued Asana bearer token and exposes `auth check` through
`commands.asana`. It does not register apps, exchange, refresh, revoke, or store OAuth tokens.
"""
