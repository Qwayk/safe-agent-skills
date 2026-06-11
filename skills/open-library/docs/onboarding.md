# Onboarding (no auth)

This tool reads Open Library public data.
You do not need API keys, OAuth, or token files.

Run once:

```bash
qwayk-open-library-safe-agent-cli --output json onboarding
```

What changes:

- Creates `.env` from `.env.example` if missing.
- Shows optional fields you can add.

Suggested minimal `.env` content:

```bash
OPEN_LIBRARY_BASE_URL=https://openlibrary.org
OPEN_LIBRARY_TIMEOUT_S=30
OPEN_LIBRARY_USER_AGENT_APP=qwayk-open-library-safe-agent-cli
OPEN_LIBRARY_CONTACT=you@example.com
```

Why `OPEN_LIBRARY_CONTACT` and `OPEN_LIBRARY_USER_AGENT_APP` matter:

- They identify your tool when contacting Open Library.
- They help with operator visibility on public requests.
- They are optional but useful for best practices on low-volume calls.

## What to ask your AI agent (examples)

- Find one book about dune and keep the result count low.
- Open the work record for one Open Library work ID.
- Look up one ISBN and show the edition record.
- Test one subject query with a small `--limit` because the subject endpoint is experimental.
