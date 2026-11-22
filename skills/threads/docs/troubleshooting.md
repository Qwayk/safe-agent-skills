# Fix a Threads error

## Setup and reads

- Run `auth check` to check the account ID and username. Check which settings file you used and whether an old `THREADS_API_TOKEN` is taking priority over the saved token.
- If access is refused, check the app permission for the command. If a call returns several pages, use the cursor before drawing conclusions from the first page. [Account setup](onboarding.md) · [API coverage](api_coverage.md)
- Use `--verbose` to see request timings or `--debug` for details when developing locally. Keep tokens, app secrets and sign-in codes private.

## Publishing

Run `posts status --threads-container-id DRAFT_ID` to see whether Threads is still processing the draft, has finished preparing it, has already published it, or found an error. The command shows the reason Threads supplies for processing errors. If the publish reply was unclear, check this status before another attempt. Meta recommends checking once a minute for up to five minutes. [Meta’s publishing help](https://developers.facebook.com/documentation/threads/troubleshooting#publishing-does-not-return-a-media-id)

If the draft is ready and the tool refused the change, read the reason and check the approval flags and the saved plan. Get a new approval if the request changed. If you have a post ID, read it with `posts get --threads-media-id POST_ID`. [Review and check changes](safety_model.md)
