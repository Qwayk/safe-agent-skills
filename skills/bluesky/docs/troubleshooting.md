# Fix a Bluesky error

- If a public request fails, check the handle and the service URL in the output. Use the [public feed example](quickstart.md#read-public-posts) with a separate settings directory if you want an anonymous request from a machine with a saved account.
- If `auth check` reports no session, use `auth login` to start one or `auth refresh` to renew it. If the app password was revoked, replace it in your local settings and sign in again. [Account setup](onboarding.md)
- If a write is refused, read the reason before trying again. Check the approval flags, and for a post, check the saved plan, account, server and text. Get a new approval if the request changed. [Safety guide](safety_model.md)
- If a write times out or returns an unclear response, read the account or record to see whether the change happened before retrying. If Bluesky limits requests, check the status and wait before sending more.
- Use `--verbose` to see request timings or `--debug` for more detail. Share only the parts needed to explain the error. Keep tokens and private account data out of the reply.
