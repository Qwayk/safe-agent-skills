# Hacker News API coverage

These ten commands cover the HTTP reads in the [official Hacker News v0 API](https://github.com/HackerNews/API). The Firebase client library's live subscriptions and private interfaces are outside this list.

The endpoint list was originally checked on 2026-05-21 at 00:00 UTC. See [test results](proof.md) for later checks. The CLI keeps the fields returned with valid items and users. In JSON mode, it formats the result, so the Firebase `print=pretty` option is unnecessary.

| Status | Method | Path | Purpose | CLI | Safety | Verification | Tests |
|---|---|---|---|---|---|---|---|
| implemented | GET | `/v0/item/{item_id}.json` | Fetch one item by ID | `hacker-news-api-tool items get --id <ITEM_ID>` | Read-only | ID matches; missing records return `ValidationError` | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/user/{user_id}.json` | Fetch one user by ID | `hacker-news-api-tool users get --id <USER_ID>` | Read-only | ID matches; missing records return `ValidationError` | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/topstories.json` | List top story IDs | `hacker-news-api-tool stories top` | Read-only | Keeps the order and accepts an empty list | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/newstories.json` | List newest story IDs | `hacker-news-api-tool stories new` | Read-only | Keeps the order and accepts an empty list | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/beststories.json` | List best story IDs | `hacker-news-api-tool stories best` | Read-only | Keeps the order and accepts an empty list | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/askstories.json` | List Ask HN story IDs | `hacker-news-api-tool stories ask` | Read-only | Keeps the order and accepts an empty list | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/showstories.json` | List Show HN story IDs | `hacker-news-api-tool stories show` | Read-only | Keeps the order and accepts an empty list | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/jobstories.json` | List job story IDs | `hacker-news-api-tool stories jobs` | Read-only | Keeps the order and accepts an empty list | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/maxitem.json` | Fetch the latest item ID | `hacker-news-api-tool maxitem get` | Read-only | Checks for a positive integer | `tests/test_run_artifacts.py` |
| implemented | GET | `/v0/updates.json` | Fetch changed item and profile IDs | `hacker-news-api-tool updates get` | Read-only | Checks both lists and keeps extra fields | `tests/test_run_artifacts.py` |
