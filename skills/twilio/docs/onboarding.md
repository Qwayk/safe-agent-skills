# Connect a Twilio account

You need Python 3.12 or newer, a Twilio Account SID, and credentials that can reach the operations you intend to use. Start with the least access that still does the job.

## Install the skill and CLI

Ask your agent to install the `twilio` skill from `Qwayk/safe-agent-skills`. If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@twilio -g -y
```

Then, from the installed skill folder:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
```

## Create the private settings file

```bash
.venv/bin/qwayk-twilio-safe-agent-cli onboarding --write-env
```

The command creates `.env` at mode `600` and refuses to overwrite an existing file. Fill these values:

```dotenv
TWILIO_ACCOUNT_SID=AC...
TWILIO_API_KEY_SID=SK...
TWILIO_API_KEY_SECRET=...
TWILIO_TIMEOUT_S=30
```

Use a Restricted API key when it grants the needed permissions. If you must use the Account Auth Token fallback, set `TWILIO_AUTH_TOKEN`; the tool reports that fallback as a warning.

Do not paste real keys, tokens, or the completed `.env` into chat. Do not commit it.

## Optional routing and OAuth

Set region and edge only as a pair:

```dotenv
TWILIO_REGION=au1
TWILIO_EDGE=sydney
```

The credentials must be valid in that region. Set `TWILIO_OAUTH_ACCESS_TOKEN` only when you need a pinned operation whose official definition requires OAuth.

## Check access

Validate the file without contacting Twilio:

```bash
.venv/bin/qwayk-twilio-safe-agent-cli auth check
```

Then run the first safe provider read:

```bash
.venv/bin/qwayk-twilio-safe-agent-cli api-v2010 fetch-account \
  --input-json examples/inputs/fetch-account.json
```

Normal output hides private fields. If this fails, use [authentication](authentication.md) and [troubleshooting](troubleshooting.md) before trying any live change.

## First agent ask

```text
Confirm the Twilio account connection, then check recent failed messages and explain the failure reasons. Do not send or change anything.
```

No live credentials or provider request were used to prove this source build. Your first account fetch is therefore the point where live access becomes verified for your setup.
