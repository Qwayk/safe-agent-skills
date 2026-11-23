# Open Library API coverage

These nine commands read Open Library's public catalog. The first coverage review was on May 21, 2026. See [test results](proof.md) for later checks.

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

Searches return `docs`, work or edition lists return `entries`, and subject lookups return `works`. A valid list can be empty. A single record includes its Open Library key. The tool keeps the fields Open Library sends with valid results.

Subject lookup is experimental. Account features, writes, batch jobs and any endpoints outside the table are outside this tool. [Open Library references](references.md)
