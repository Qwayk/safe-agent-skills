# Open Library test results

## November 23, 2026 local checks

Both local copies passed 14 offline tests after a fresh install. With saved or simulated replies, I used the installed tool from an empty folder to search for Dune, open the matching work, handle an empty result, and reject invalid replies. A wrong kind of record ID failed before sending a request. The `--timeout-s` flag worked with an invalid timeout in the settings file.

A fresh local Codex install matched all 41 files under `open-library`. Before these changes, a live search from the published install found *Dune*, *Dune Messiah*, and *Children of Dune* without a settings file.

## May 21, 2026 checks

Codex checked version `0.1.0` with the public API at `https://openlibrary.org`. Ten offline tests passed.

### Commands used in the original checks

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

## Saved replies

- [version](examples/outputs/version.json)
- [onboarding](examples/outputs/onboarding.json)
- [search books](examples/outputs/search_books.json)
- [search authors](examples/outputs/search_authors.json)
- [works get](examples/outputs/works_get.json)
- [works editions list](examples/outputs/works_editions_list.json)
- [editions get](examples/outputs/editions_get.json)
- [isbn lookup](examples/outputs/isbn_lookup.json)
- [authors get](examples/outputs/authors_get.json)
- [authors works list](examples/outputs/authors_works_list.json)
- [subjects get](examples/outputs/subjects_get.json)

## Run the tests

Run these commands inside the tool folder.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
```

See the [command guide](command_reference.md) for setup and errors, and [API coverage](api_coverage.md) for the available reads.
