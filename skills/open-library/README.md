# Open Library

**Capability:** Read-only

Open Library is useful when you want book and author research from a public catalog instead of a general web search. It is good for checking what editions exist, resolving an ISBN, finding an author's work, or building a small reading or research list from catalog records.

This skill lets an agent search public Open Library data for books, authors, works, editions, ISBNs, and subjects. Ask it for jobs like "Find books about Dune and show the best matches", "Open this author record and list their works", or "Look up this ISBN and explain the edition record."

No login or API key is needed. The tool is read-only, and Open Library expects these public endpoints to be used for real-time, low-volume lookups rather than bulk downloading.

A good first ask is: "Search Open Library for books about Dune, show five useful matches, and open the most relevant work record."

## Start here first

- Want ideas for real Open Library research? [What you can do with Open Library](docs/use_cases.md)
- Need the shortest setup path? [Use Open Library with no account](docs/onboarding.md)
- Want the safety story first? [How this skill stays read-only](docs/safety_model.md)

If you already want exact commands, jump straight to [Quickstart](docs/quickstart.md) and the [Command guide](docs/command_reference.md).

## What this skill helps with

- Search books by title, topic, language, or other supported fields.
- Find authors and list their works.
- Open a work or edition record when you already have the Open Library ID.
- Resolve an ISBN into a public catalog record.
- Explore a subject carefully when a small test query is enough.

## What access this skill needs

- No Open Library account.
- No API key.
- Optional `.env` settings only if you want to set the base URL, timeout, app name, or contact email for best-practice public requests.

## Install and first run

Install slug: `open-library`

Ask your agent to install the `open-library` skill from `Qwayk/safe-agent-skills`.

If new skills do not appear automatically, reopen the app or attach the skill to the current workspace if your host needs that.

If your host does not let the agent install skills directly, run:

```bash
npx skills add Qwayk/safe-agent-skills@open-library -g -y
```

Then try a safe first ask like:

```text
Search Open Library for books about Dune, show five useful matches, and open the most relevant work record.
```

## How this skill stays safe

- It is read-only by design.
- It uses public Open Library endpoints.
- It does not sign in, create records, edit records, or delete anything.
- It exposes named commands only, not a raw "call anything" API bridge.
- List-style calls should stay small and low-volume.

## What it covers today

This skill covers:

- book search
- author search
- work lookup
- work edition lists
- edition lookup
- ISBN lookup
- author lookup
- author works lists
- subject lookup for careful exploration

## What happens before live changes

There are no live changes in this skill. It reads public catalog data and returns structured output.

## What proof it leaves behind

- Normal reads return machine-readable JSON you can review or save.
- The proof pack shows smoke commands and example outputs.
- The API coverage page lists every supported endpoint and command.
- The docs and tests live with the tool so the public claims can be checked.

## Limits

- Open Library public endpoints are for low-volume real-time use, not bulk downloading.
- Subject lookup is marked experimental in this tool.
- Catalog records can be incomplete or inconsistent because Open Library is a public catalog.
- This skill cannot edit Open Library data or use account-only features.

## Helpful docs

- [Browse all Open Library docs](docs/README.md)
- [Quickstart](docs/quickstart.md)
- [Command guide](docs/command_reference.md)
- [Proof and verification](docs/proof.md)
- [API coverage](docs/api_coverage.md)
