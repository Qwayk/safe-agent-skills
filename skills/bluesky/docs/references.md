# References

- Provider: Bluesky / atproto lexicon APIs
- Last verified (UTC): 2026-05-25

Official sources used for this tool:
- https://docs.bsky.app/docs/advanced-guides/api-directory — reason: official hosts, routing, and auth guide — last verified (UTC): 2026-05-25
- https://github.com/bluesky-social/bsky-docs/tree/main/docs/api — reason: official HTTP reference page inventory for callable XRPC methods — last verified (UTC): 2026-05-25
- https://github.com/bluesky-social/atproto/tree/main/lexicons — reason: canonical official lexicon schemas and callable method definitions — last verified (UTC): 2026-05-25

Current inventory snapshot:
- Callable official lexicons: 304
- HTTP reference page coverage: 222
- Lexicon-only callable rows: 82

Important interpretation note:
- Record lexicons like `app.bsky.feed.post` and `app.bsky.graph.follow` are official schemas, but they are not callable XRPC methods. This tool exposes them through official repository methods such as `com.atproto.repo.createRecord`, `putRecord`, and `applyWrites` instead of inventing fake extra endpoint rows.
