# API coverage

Last audited/verified (UTC): 2026-05-21T00:00:00Z

This tool targets the official Hacker News Firebase API.

## Coverage definition

Coverage is defined against the official Hacker News API documentation listed in `docs/references.md`.

This ledger is considered complete when every documented v0 HTTP read endpoint appears here and maps to a named CLI command.

Out of scope:
- Firebase client SDK subscriptions and change listeners that are not separate documented HTTP endpoints for a shell CLI.
- Any undocumented, legacy, or private Hacker News interfaces.

Notes:
- This tool is read-only.
- In `--output json` mode, every invocation prints exactly one JSON object.
- The Firebase `print=pretty` query option is not exposed because the CLI already emits deterministic formatted JSON.

## Ledger

| Status | Method | Path | Purpose | CLI | Safety | Verification | Tests |
|---|---|---|---|---|---|---|---|
| implemented | GET | `/v0/item/{item_id}.json` | Fetch one item by id | `hacker-news-api-tool items get --id <ITEM_ID>` | Read-only | Response returned as-is; `null` becomes `NotFound` | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/user/{user_id}.json` | Fetch one user by id | `hacker-news-api-tool users get --id <USER_ID>` | Read-only | Response returned as-is; `null` becomes `NotFound` | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/topstories.json` | List top story ids | `hacker-news-api-tool stories top` | Read-only | Response returned as-is | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/newstories.json` | List newest story ids | `hacker-news-api-tool stories new` | Read-only | Response returned as-is | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/beststories.json` | List best story ids | `hacker-news-api-tool stories best` | Read-only | Response returned as-is | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/askstories.json` | List Ask HN story ids | `hacker-news-api-tool stories ask` | Read-only | Response returned as-is | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/showstories.json` | List Show HN story ids | `hacker-news-api-tool stories show` | Read-only | Response returned as-is | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/jobstories.json` | List job story ids | `hacker-news-api-tool stories jobs` | Read-only | Response returned as-is | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/maxitem.json` | Fetch the current max item id | `hacker-news-api-tool maxitem get` | Read-only | Response returned as-is | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/updates.json` | Fetch changed item ids and profile ids | `hacker-news-api-tool updates get` | Read-only | Response returned as-is | `tests/test_run_artifacts.py` |
