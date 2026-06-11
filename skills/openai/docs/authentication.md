# Authentication

This tool uses an API key stored locally in `.env` (gitignored).

1) Copy `.env.example` → `.env`.
2) Paste your OpenAI API key next to `OPENAI_API_KEY=`.
3) Optionally set `OPENAI_ORGANIZATION_ID` / `OPENAI_PROJECT_ID` if you target org/project scoped features.
4) Run `openai-api-tool --output json auth check` to confirm your configuration (it reports which fields are populated). Add the `--live` flag to make a real `/models` call and get `live_ok`/error details when you need to prove the key works.

Important:
- Never commit `.env`.
- Never print `OPENAI_API_KEY` or other secrets in logs.
