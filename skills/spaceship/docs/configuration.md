# Configuration

Keep account credentials in a local `.env` file:

```text
SPACESHIP_API_KEY=<your key>
SPACESHIP_API_SECRET=<your secret>
SPACESHIP_TIMEOUT_S=30
```

`SPACESHIP_TIMEOUT_S` is optional. Operating-system values override the same keys in `.env`.

The production API base is fixed to `https://spaceship.dev/api`. The CLI does not provide a general base-URL override. Test code can inject a fake transport without changing production configuration.

Write plans, receipts, audit logs, and run history stay under the local paths you choose or `.state/runs/`. Keep `.env`, `.state`, and any real request-body files out of public or shared copies when they contain private data.
