# Configuration

The default settings file is `.env` in the current directory. Choose another file by putting `--env-file FILE` before the command group:

```bash
qwayk-twilio-safe-agent-cli --env-file .env.us1 auth check
```

Environment variables already set in the operating system take precedence over values in the selected file.

## Settings

| Variable | Used for |
| --- | --- |
| `TWILIO_ACCOUNT_SID` | Account scope for Basic-auth operations |
| `TWILIO_API_KEY_SID` | Preferred Basic-auth username; must be paired with its secret |
| `TWILIO_API_KEY_SECRET` | Preferred Basic-auth password |
| `TWILIO_AUTH_TOKEN` | Warned Basic-auth fallback |
| `TWILIO_OAUTH_ACCESS_TOKEN` | Only pinned OAuth operations |
| `TWILIO_REGION` | Optional Twilio region; must be paired with edge |
| `TWILIO_EDGE` | Optional Twilio edge; must be paired with region |
| `TWILIO_TIMEOUT_S` | Positive request timeout in seconds; default `30` |

`TWILIO_ACCOUNT_SID` must be a 34-character SID beginning with `AC`. `TWILIO_API_KEY_SID` must be a 34-character SID beginning with `SK`. An API key SID without its secret, or a region without an edge, is refused before any request.

## Private local files

Run this once to create a mode-`600` `.env` template:

```bash
qwayk-twilio-safe-agent-cli onboarding --write-env
```

The tool refuses to overwrite an existing env file. `.env`, `.state/`, and `.venv/` are ignored by this repository.

Plan and sensitive-output files are created only when you give their output flag. Every live apply requires `--receipt-out`. The receipt destination must be new: the tool creates it at mode `600` before HTTP and refuses an existing path or a destination it cannot create. Plan and sensitive-output files are also written at mode `600`. Files passed with `--plan-in` or `--snapshot-in` must already have mode `600` or the tool refuses them before contacting Twilio.

## Output settings

JSON is the default and prints one compact object for agent use. `--output text` prints the same structured result as indented JSON. `--verbose` adds only the HTTP method, Twilio host, and status on stderr; it does not print headers, query values, or request bodies.
