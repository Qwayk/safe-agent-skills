# Authentication

Hacker News does not need an account connection for its public read work. That is the most important setup fact: an agent can use the public API without an API key, bearer token, or OAuth approval.

The only useful check is whether your machine can reach Hacker News. Run the safe auth or connection check before asking for real results, then continue with the normal read commands.

A good first auth check is: "Confirm Hacker News does not need credentials, run the safe connection check, and tell me whether the public API is reachable."

## Setup details

`auth check` is still useful:
- It performs one safe live read against `maxitem.json`.
- It proves the API root is reachable from your machine.
- It keeps the same trust shape as other Qwayk tools without inventing a fake secret flow.

In plain English: there is nothing to connect. If the connection check works, the public API is reachable.
