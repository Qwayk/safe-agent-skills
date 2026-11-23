# Connect your Qdrant Cloud account

Get a Cloud Management Key from Access Management in the Qdrant Cloud Console. [Qdrant Cloud API setup](https://qdrant.tech/documentation/cloud-api/)

Open the [tool’s source folder](https://github.com/Qwayk/safe-agent-skills/tree/main/skills/qdrant-cloud). From that folder, install the CLI with Python 3.12 or later and create your local settings file:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/qdrant-cloud-api-tool onboarding
```

Put the key in the file that setup shows. Keep the file and key out of chat and Git. Keys can contain characters such as `|`. Put single quotes around the value when your shell will read the file:

```dotenv
QDRANT_CLOUD_API_KEY='your_real_key_here'
```

For a different file, put `--env-file "path/to/qdrant.env"` before `onboarding`. The tool creates a private starter file if it is missing and shows both commands with that path. Use `onboarding --no-write-env` to see the setup steps without creating a file.

`auth check` checks the local settings. When you approve live access, `--live auth check` checks the key against Qdrant, and `--live account-v1 list-accounts` lists the accounts the key can access. The first account and cluster reads are in the [quickstart](quickstart.md).

## Settings and common problems

- A value in your shell takes priority over the same setting in the file.
- The default API address is `https://api.cloud.qdrant.io`. Set `QDRANT_CLOUD_API_BASE_URL` only when you need a different address, and use a test key for a local test server.
- The default timeout is 30 seconds. Set `QDRANT_CLOUD_TIMEOUT_S` or pass `--timeout-s` for one command.
- For a rejected key, check the file you selected and the key’s account access. The Cloud API uses the `Authorization: apikey <KEY>` header.
- If a write stops, read the reason before trying again. [Which approvals are needed](safety_model.md)
- `--verbose` shows request start and end messages. `--debug` shows a Python error trace for local debugging. Check output for private details before sharing it.
