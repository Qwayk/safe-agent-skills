# Use Open Library with no account

Open Library uses public data. You do not need API keys, OAuth, or token files to search books, authors, editions, and identifiers.

No secrets are needed for the first run. If the tool creates a local `.env` file, treat it as local setup only; it should not contain a private service token.

Start by checking the exact book, author, or edition match before relying on the result.

## First setup

Install the tool locally, then run:

```bash
qwayk-open-library-safe-agent-cli --output json onboarding
qwayk-open-library-safe-agent-cli --output json auth check
```

The default public API root is:

```dotenv
OPEN_LIBRARY_BASE_URL=https://openlibrary.org
```

You can leave the other `.env` values alone unless you want to set a custom timeout or contact value for your local requests.

## What to ask your AI agent (examples)

- Find one book about dune and keep the result count low.
- Open the work record for one Open Library work ID.
- Look up one ISBN and show the edition record.
- Test one subject query with a small `--limit` because the subject endpoint is experimental.

## What to avoid

- Do not ask it to change Open Library records. This tool is for public reads.
- Do not trust a title match alone when the edition matters. Ask for the author, work ID, edition ID, ISBN, and publication details.
