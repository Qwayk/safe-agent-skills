# API coverage

Open Library coverage shows exactly what the shipped commands can do with public books, authors, editions, subjects, and ISBN data. Start here when an ask sounds possible but you need to know whether it is already shipped, read-only, plan-first, gated, excluded, or outside the tool.

Read the shipped command rows first, then check the excluded or not-yet-live rows before asking an agent to act. If an endpoint or workflow is not listed here, do not assume the skill supports it.

A good first coverage check is: "Check whether the shipped commands can search books, open one work and edition, and show which Open Library endpoints are out of scope."

## Coverage notes

Last audited (UTC): 2026-05-21

## Scope summary

- Provider: Open Library
- Read-only: yes
- Auth: none required
- Experimental: `subjects` endpoint
- No raw request and no write commands

## Endpoint coverage

| Endpoint | CLI command | Params supported |
|---|---|---|
| `GET /search.json` | `search books` | `q`, `fields`, `sort`, `lang`, `limit`, `page`, `offset` |
| `GET /search/authors.json` | `search authors` | `q`, `limit`, `offset` |
| `GET /works/{work_id}.json` | `works get` | `{work_id}` |
| `GET /works/{work_id}/editions.json` | `works editions list` | `limit`, `offset` |
| `GET /books/{edition_id}.json` | `editions get` | `{edition_id}` |
| `GET /isbn/{isbn}.json` | `isbn lookup` | `{isbn}` |
| `GET /authors/{author_id}.json` | `authors get` | `{author_id}` |
| `GET /authors/{author_id}/works.json` | `authors works list` | `limit`, `offset` |
| `GET /subjects/{subject}.json` | `subjects get` | `details`, `ebooks`, `published_in`, `limit`, `offset` |

## Explicitly out of scope

- no auth commands
- no raw request commands
- no jobs/runs
- no apply/dry-run
- no write commands
