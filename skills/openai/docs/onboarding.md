# Set up the OpenAI API key

Run `openai-api-tool onboarding` to create a private `.env` in the current folder. To choose another file, run `openai-api-tool --env-file "account settings.env" onboarding`. If you already have a settings file, use it. Setup prints the next command with the same path.

Copy a key for the right project from [OpenAI API keys](https://platform.openai.com/api-keys). Put it in `OPENAI_API_KEY` in your settings file. Keep the key out of chat, command arguments, and shared files.

| Setting | When to use it |
|---|---|
| `OPENAI_API_KEY` | Needed before a live request |
| `OPENAI_ORGANIZATION_ID` and `OPENAI_PROJECT_ID` | Set these when you need to choose an organization or project explicitly |
| `OPENAI_API_BASE_URL` | Defaults to `https://api.openai.com/v1`. Change it only for an OpenAI destination you intend to use |
| `OPENAI_TIMEOUT_S` | Defaults to 30 seconds. Use a positive number |

Values set in the shell take priority over values in the file. The local `auth check` tells you what is set. Add `--live` before `auth check` to check whether the key can list models. If the live check fails, check the selected file, project, and key permissions. Keep the HTTP status when you ask for help.

[First commands](../README.md#get-started) · [Command options](command_reference.md)
