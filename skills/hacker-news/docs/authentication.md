# Authentication

This tool does not use authentication.

The official Hacker News API is public and read-only, so there is no API key, bearer token, or OAuth flow to configure.

`auth check` is still useful:
- It performs one safe live read against `maxitem.json`.
- It proves the API root is reachable from your machine.
- It keeps the same trust shape as other Qwayk tools without inventing a fake secret flow.

In plain English: there is nothing to connect. If the connection check works, the public API is reachable.
