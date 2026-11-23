# API coverage

The tool uses `https://account.giantpanda.com` and sends `Authorization: Token <GIANTPANDA_API_TOKEN>`. It stops on a redirect.

| Endpoint | What it does | CLI command | Checks |
|---|---|---|---|
| `GET /api/v1/domains/stats/` | Read parked-domain stats for a date range, with optional paging | `domains stats` | One live read on August 11, 2026, plus offline tests |
| `POST /api/v1/domains/add/` | Add the domains in an approved plan | `domains add` | Offline tests with replies based on the API docs |

GiantPanda’s API docs describe which names were created and which already existed. The tool checks those lists against the approved names. The stats route is for reporting. Check account membership in the dashboard when the add result is unclear. [API references](references.md) · [Dated checks](proof.md)
