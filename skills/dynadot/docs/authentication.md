# Authentication

Dynadot API3 uses an **API key**.

You store it locally in your `.env` file (gitignored).

Notes:
- The Dynadot API key is sent as a **URL query parameter** (`key=...`), so URLs must be treated as sensitive.
- This tool redacts `key=...` anywhere it might appear in logs or errors.
