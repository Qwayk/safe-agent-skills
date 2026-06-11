# Safety model

This tool is intentionally read-only.

- No authentication secrets are required.
- No `--apply`, `--yes`, or write workflow exists.
- The tool only performs `GET` requests to the public Hacker News API.
- In `--output json` mode, every command prints exactly one JSON object.
- Missing items or users come back as clear JSON errors instead of silent `null` payloads.

What this means in plain English:
- The tool can fetch public Hacker News data.
- The tool cannot change Hacker News data.
- The tool cannot leak an API key because there is no API key in this workflow.
