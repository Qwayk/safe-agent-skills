# Fix an Instagram error

## Setup and reads

- Run `auth check` to see the account ID and username. Use `auth token status` to see where the token is saved. A token in your settings or shell takes priority over the saved file.
- If the token has expired, get a fresh one. Use `auth token refresh` with approval to renew an eligible token before it expires. [Account setup](onboarding.md)
- If profile reads work and another command fails, check the permission for that job and whether it is available with Instagram Login. [API coverage](api_coverage.md)

Use `--verbose` to see request timings or `--debug` for more detail when working locally. Keep tokens and codes private.

## Publishing

Run `media container get --container-id DRAFT_ID` to check whether Instagram is processing the draft, has it ready, has already published it, or returned an error. Check this before trying again if the publish reply was lost. Meta recommends checking once a minute for up to five minutes. [Meta’s draft status guide](https://developers.facebook.com/documentation/instagram-platform/content-publishing#container-publishing-status)

If the command refuses to apply a plan, read the reason and check the approval flags and account. Preview again if the request changed. If you have a published post ID, check it with `media get --media-id POST_ID`. [Review and check changes](safety_model.md)
