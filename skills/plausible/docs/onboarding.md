# Connect your Plausible account

Start with a **Stats API key** for the team that owns the site. In Plausible, select the team, open your account settings, choose **API Keys**, and create a Stats API key. Copy it while it is visible. Its access is limited to sites that team owns. [Plausible Stats API](https://plausible.io/docs/stats-api#authentication)

From the tool folder, copy the example to a new local settings file. If you already have a file, open that file and use its path in the commands.

```bash
umask 077
cp -n .env.example .env
```

- Set `PLAUSIBLE_SITE_ID` to the site's domain as it appears in Plausible.
- Set `PLAUSIBLE_API_KEY` to the key. Keep it out of chat and Git.
- Keep `PLAUSIBLE_BASE_URL=https://plausible.io` for hosted Plausible. For a self-hosted instance, enter that instance's base address.
- `PLAUSIBLE_TIMEOUT_S` defaults to 30 seconds. If your instance uses Cloudflare Access, set `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` to its existing service token values. The longer `CLOUDFLARE_ACCESS_CLIENT_ID` and `CLOUDFLARE_ACCESS_CLIENT_SECRET` names also work.
- Values set in your shell take priority over values in the file. If the tool connects somewhere unexpected, check the shell settings and the file selected by `--env-file`.

Run the connection check with the same file. It asks Plausible for the last seven days of visitor data and checks that the response contains Stats API results.

```bash
plausible-api-tool --env-file .env auth check
```

A Stats key can also use supported read-only Sites API commands. Hosted site changes need a Sites API key for the owning team on a plan with that access. Use a separate local settings file when the job needs a different key. Some destructive actions require a key from the site owner. [Plausible Sites API](https://plausible.io/docs/sites-api)

## If the check fails

- **401 or 403.** Check the file path, key type, site, and team. If Cloudflare shows a sign-in page, check the instance address and the existing Cloudflare Access token.
- **Unexpected reply.** Check that the address points to the Plausible API. In `auth check`, the Stats API result is what confirms account access. The optional health check can fail on an instance that restricts or lacks that endpoint.
- **Query error.** Use [query validation](queries.md#validate-a-query-json-file) to check the local JSON. If Plausible says that a goal is missing, verify its exact name in the right site. Adding one is a site change and needs approval.
- **Debugging.** `--verbose` prints request timing and status to stderr. `--debug` shows a Python traceback. Keep your settings and output files private. Check the [safety guide](safety_model.md) before retrying a write.
