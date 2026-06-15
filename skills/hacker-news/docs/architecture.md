# Architecture

Hacker News is built as a small command-line tool for public stories, comments, users, and item changes. The architecture is intentionally plain: commands parse the user request, configuration loads only the needed account settings, the client layer talks to the API, and the output layer returns one predictable JSON result.

This matters when an agent is using the skill for real work. You can see where credentials are loaded, where HTTP requests happen, where local plans or receipts are saved, and where safety checks stop a risky action before it reaches Hacker News.

A good architecture check is: "Show me which layer handles configuration, which layer sends the API request, and where a plan or receipt would be saved for Hacker News."

## Runtime layers

- `cli.py`: argument parsing, shared flags, JSON-safe errors, and command routing
- `hacker_news_client.py`: small Hacker News API wrapper for URL building and JSON reads
- `config.py`: `.env` parsing and API root validation
- `http.py`: HTTP wrapper around `requests`
- `output.py`: deterministic stdout contract
- `audit_log.py`: optional JSONL audit events with redaction
- `errors.py`: consistent error types
