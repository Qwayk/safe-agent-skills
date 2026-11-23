# Open Library commands

Start with the [quickstart](quickstart.md) if you need to install the tool. Put global options before the command, for example `qwayk-open-library-safe-agent-cli --output json search books --q "dune" --limit 3`.

## Searches and lookups

Add one of these commands after `qwayk-open-library-safe-agent-cli`.

```text
search books --q <text> [--fields <fields>] [--sort <sort>] [--lang <lang>] [--limit N] [--page N] [--offset N]
search authors --q <text> [--limit N] [--offset N]
works get <work-id>
works editions list <work-id> [--limit N] [--offset N]
editions get <edition-id>
isbn lookup <isbn>
authors get <author-id>
authors works list <author-id> [--limit N] [--offset N]
subjects get <subject> [--details] [--ebooks] [--published-in <year-or-range>] [--limit N] [--offset N]
```

Work IDs end in `W`, edition IDs in `M`, and author IDs in `A`. You can also pass a link to the matching record. Use `--lang fr` to prefer a French edition. To require a French edition, add `language:fre` to the search query. On book searches, use `--page` starting at 1 or `--offset` to skip records. Open Library calls subject lookup experimental. [Search options](https://openlibrary.org/dev/docs/api/search) · [Subjects API](https://openlibrary.org/dev/docs/api/subjects)

## Optional settings

The default address is `https://openlibrary.org`. The default timeout is 30 seconds. Use `--timeout-s <SECONDS>` to set the wait for one run. That flag takes priority over the saved timeout.

You can pass a JSON settings file with `--config <PATH>`. Values in that file take priority over the shell and the settings file. In the shell or a `.env` file, use the names below. Shell values take priority over the `.env` file. Use `--env-file <PATH>` to read a different file.

| JSON key | Shell or .env setting | What it controls |
| --- | --- | --- |
| `base_url` | `OPEN_LIBRARY_BASE_URL` | API address |
| `timeout_s` | `OPEN_LIBRARY_TIMEOUT_S` | How long to wait, in seconds |
| `user_agent_app` | `OPEN_LIBRARY_USER_AGENT_APP` | App name sent with the request. The default is `qwayk-open-library-safe-agent-cli`. |
| `contact` | `OPEN_LIBRARY_CONTACT` | Optional contact Open Library can use if it needs to reach you |

The optional `onboarding` command shows settings help and can create a local file. It copies a settings template when available or creates an empty file. The first search can use the built-in defaults.

- `--version` shows the installed version.
- `--output json|text` chooses the output format. JSON is the default.
- `--log-file <PATH>` saves a local log as one JSON object per line.
- `--verbose` shows HTTP details on standard error. `--debug` shows an error trace.

## If a read fails

Check the exact error and the record ID. If a search returns an empty list, check the title spelling, try fewer search terms or return to the first page. An unexpected reply is reported as an error.

Keep requests small. Open Library lists a limit of one request per second for requests without contact details and three per second for requests that identify the app and include a contact email. If the service returns HTTP 429, wait before trying again. Reuse recent results where you can. [Open Library request limits](https://openlibrary.org/developers/api#rate-limits)
