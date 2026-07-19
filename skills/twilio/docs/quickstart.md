# Get your first Twilio account result

Your first useful result is a live account read that confirms the tool can reach Twilio without changing, sending, buying, or deleting anything.

From the tool folder, install the source with Python 3.12 or newer:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
```

Create a private `.env` template:

```bash
.venv/bin/qwayk-twilio-safe-agent-cli onboarding --write-env
```

Fill these three values in `.env`:

```dotenv
TWILIO_ACCOUNT_SID=AC...
TWILIO_API_KEY_SID=SK...
TWILIO_API_KEY_SECRET=...
```

The tool refuses to overwrite an existing `.env`. The generated file is readable only by your local user.

Check the settings without contacting Twilio:

```bash
.venv/bin/qwayk-twilio-safe-agent-cli auth check
```

Then fetch the connected account through the fixed Twilio command:

```bash
.venv/bin/qwayk-twilio-safe-agent-cli api-v2010 fetch-account \
  --input-json examples/inputs/fetch-account.json
```

The command prints one JSON object. A successful result has `ok: true`, an HTTP status, and the account response with sensitive values hidden. It does not change the account.

If you genuinely need the full response, save it to a protected local file instead of normal output:

```bash
.venv/bin/qwayk-twilio-safe-agent-cli api-v2010 fetch-account \
  --input-json examples/inputs/fetch-account.json \
  --sensitive-out .state/account.json
```

The saved file is created with mode `600`, which limits access to your local user. Do not commit it or paste it into chat.

You can also confirm the pinned command boundary without credentials:

```bash
.venv/bin/qwayk-twilio-safe-agent-cli inventory summary
```

To see the exact accepted input before preparing a command, inspect its fixed contract locally:

```bash
.venv/bin/qwayk-twilio-safe-agent-cli inventory show \
  --command api-v2010.create-message
```

Once the account read works, ask your agent: "Check recent failed messages and explain which failures need action. Do not send or change anything." See [more useful asks](use_cases.md) or the [exact command grammar](command_reference.md).
