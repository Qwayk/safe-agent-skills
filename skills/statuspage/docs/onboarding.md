# Set up a public Statuspage URL

Give your agent the root URL of the vendor’s public Statuspage, such as `https://status.atlassian.com`. The tool reads public data without an account or API key. For one check, pass the URL with `--base-url` and follow the [Quickstart](quickstart.md).

## Save a page you check often

From the folder that contains the tool, copy the example:

```bash
cp .env.example .env
```

Set `STATUSPAGE_BASE_URL=https://status.atlassian.com` using the page you want. The optional `STATUSPAGE_TIMEOUT_S` sets how many seconds a request can wait. The default is 30 seconds.

The CLI reads `.env` in the folder you run it from. Use `--env-file` to pick another file. You can also use `--config` with a JSON file that holds defaults:

```json
{
  "base_url": "https://status.atlassian.com",
  "timeout_s": 30
}
```

The command flag takes priority, followed by the shell variable, the env file, then the JSON file. Use `--base-url` or `--timeout-s` to override an older setting for one run.

## If a request fails

- If the URL is missing, pass the public page root with `--base-url`. Leave out any path, query, or fragment.
- If a request times out, check that the page opens, then try a longer `--timeout-s` if needed.
- If the API returns an error or leaves out required data, keep the error message and open the public page to see what it shows. Add `--verbose` before the command for HTTP details on stderr. Use `--debug` if you need a traceback.

`statuspage-api-tool auth check` explains the access the tool needs on your machine. To check that a page is reachable, run `summary get` with its URL.
