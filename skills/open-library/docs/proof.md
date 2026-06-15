# Proof and verification

Open Library proof should answer a simple question: what has actually been checked for public books, authors, editions, subjects, and ISBN data, and what can still fail because of public API limits, changed upstream data, or reviewer judgment?

You do not need to run every command before using the skill. Start with the evidence that matters most: the last verified date, the smoke checks, the saved example outputs, and the known failure cases.

If you only check one thing, check the saved book, author, edition, ISBN, and subject examples before trusting library research.

## Last verified

- Date (UTC): 2026-05-21
- Verified by: Codex
- Tool version: 0.1.0
- API model: Open Library public endpoints
- Base URL: https://openlibrary.org

## Blessed local validation

Run inside the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

Result on 2026-05-21:

- `.venv/bin/python -m unittest -q` -> `OK` with 10 tests

## Smoke checks

- `qwayk-open-library-safe-agent-cli --output json --version`
- `qwayk-open-library-safe-agent-cli --output json onboarding`
- `qwayk-open-library-safe-agent-cli --output json search books --q "dune" --limit 1`
- `qwayk-open-library-safe-agent-cli --output json works get OL45804W`
- `qwayk-open-library-safe-agent-cli --output json works editions list OL45804W --limit 1`
- `qwayk-open-library-safe-agent-cli --output json editions get OL7353617M`
- `qwayk-open-library-safe-agent-cli --output json isbn lookup 9780140328721`
- `qwayk-open-library-safe-agent-cli --output json authors get OL34184A`
- `qwayk-open-library-safe-agent-cli --output json authors works list OL34184A --limit 1`
- `qwayk-open-library-safe-agent-cli --output json subjects get foxes --limit 1`

## Committed example outputs

- `docs/examples/outputs/version.json`
- `docs/examples/outputs/onboarding.json`
- `docs/examples/outputs/search_books.json`
- `docs/examples/outputs/search_authors.json`
- `docs/examples/outputs/works_get.json`
- `docs/examples/outputs/works_editions_list.json`
- `docs/examples/outputs/editions_get.json`
- `docs/examples/outputs/isbn_lookup.json`
- `docs/examples/outputs/authors_get.json`
- `docs/examples/outputs/authors_works_list.json`
- `docs/examples/outputs/subjects_get.json`

## What can go wrong

- No-auth public endpoints can still enforce network-level blocking or strict rate behavior.
- Invalid OLIDs or ISBNs will fail fast before the request is sent.
- `subjects` is experimental and can change without warning.
- Avoid large `--limit` values, broad queries, and bulk-style repeated lookups.

## Links

- `docs/references.md`
- `docs/api_coverage.md`
- `docs/engineering_notes.md`
