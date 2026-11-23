# Connect your Unsplash Access Key

Use an Access Key for your Unsplash API application. Keep the key in a private settings file on your machine.

```bash
unsplash-api-tool --env-file unsplash.env onboarding
```

Open the file the command names and put your key after `UNSPLASH_ACCESS_KEY=`. Then run the connection check it prints.

```bash
unsplash-api-tool --env-file unsplash.env auth check
```

The connection check reads one photo record. Use the same `--env-file` on the commands that follow. The default file is `.env`. Use `onboarding --no-write-env` to check what is missing without creating a file.

## Other ways to set the key

You can also pass the key in the `UNSPLASH_ACCESS_KEY` environment variable or import a local JSON file containing an `access_key` field.

```bash
unsplash-api-tool --env-file unsplash.env auth key set --file auth.json
unsplash-api-tool --env-file unsplash.env auth key status
```

The import saves the key in `.state/auth.json` beside your settings file. A key set in the environment or settings file takes priority. Keep private settings and key files out of chat and Git.

## Optional settings

| Setting | Default |
| --- | --- |
| `UNSPLASH_API_BASE_URL` | `https://api.unsplash.com` |
| `UNSPLASH_TIMEOUT_S` | 30 seconds |

The tool sends the Access Key with `Authorization: Client-ID …` and uses API version 1. It supports photo and other public reads through that key. OAuth and private account actions are outside this tool's scope.

## When the connection fails

- For a missing key or HTTP 401, check the selected settings file and the key for your API application.
- For HTTP 429, check your API request limit before continuing. [Unsplash rate limits](https://unsplash.com/documentation#rate-limiting)
- Use `--verbose` for request lines or `--debug` for a Python traceback while debugging. Keep private settings out of shared logs.
