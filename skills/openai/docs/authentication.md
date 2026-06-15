# Authentication

OpenAI authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because models, files, batches, fine-tuning, vector stores, assistants, and generated API calls can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required OpenAI environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Setup details

1) Copy `.env.example` → `.env`.
2) Paste your OpenAI API key next to `OPENAI_API_KEY=`.
3) Optionally set `OPENAI_ORGANIZATION_ID` / `OPENAI_PROJECT_ID` if you target org/project scoped features.
4) Run `openai-api-tool --output json auth check` to confirm your configuration (it reports which fields are populated). Add the `--live` flag to make a real `/models` call and get `live_ok`/error details when you need to prove the key works.

Important:
- Never commit `.env`.
- Never print `OPENAI_API_KEY` or other secrets in logs.
