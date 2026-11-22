# Contentsquare test results

The June 25, 2026 source build used simulated replies and redacted examples. Testing against a live Contentsquare account is still open. To check live access, get a token and run one [export read](quickstart.md) in a project you recognize.

## November 22, 2026 local checks

- Both copies passed 40 tests from the checkout and from a fresh install outside it. Both installed copies loaded all 82 API entries. The tests used simulated Contentsquare replies, and the network check recorded zero connection attempts.
- The source archives include the skill, guides, settings example and saved examples. I checked 80 local links and parsed 44 command examples from each copy.
- A different project, OAuth credential, scope, request or body stops before the tool requests a token. An approved write goes out once per apply. If the reply is lost, the receipt tells you to check Contentsquare before trying again.
- A rejected speed report returns an error. Export runs show their state and whether there are download links. An empty, short or error-page download leaves the existing file alone. Enrichment accepts the documented [HTTP 200 reply](https://docs.contentsquare.com/en/api/enrichment/sending-enrichment-data-batches-cs/#response) when it has no body.
- Python type checks passed. Five existing Ruff style findings remain.

## June 25, 2026 source build

- Version `0.1.0`. Codex installed the source and recorded 46 passing unit tests, a new-tool audit, a Control Room alignment audit and a clean `git diff --check`.
- The tool mapped 82 documented server-side entries. Local tests checked the API-family scopes, explicit scope overrides, account-level `project_id`, the credential body for `auth me`, and the rule against combining Enrichment with other scopes. The auth checks kept the client secret and token out of their output.
- Tests checked that the CLI sends official query names such as `projectId`, `startDate`, `endDate`, `segmentIds`, `goalId`, `period`, `ids`, `state`, `order`, `format`, `frequency`, `scope`, `from`, and `to`.
- Tests covered plan previews and required confirmation, the run lookup's `files[].url` field, and selecting one of several files by `--file-index` or `--part-id`. The public docs were also checked for old starter copy and commands that would bypass the named operations.

## Run the checks locally

From the tool folder:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest -q
.venv/bin/contentsquare-safe-cli --output json --version
```

Use `contentsquare-safe-cli --output json auth check` when you have approved access to a real account. This obtains a token. Follow it with a read from the API and project you plan to use.

## Saved examples from the first build

- [Version](examples/outputs/version.json)
- [Connection check](examples/outputs/auth_check.json)
- [Export jobs](examples/outputs/data_export_list_jobs.json)
- [Bounce rate](examples/outputs/metrics_site_bounce_rate.json)
- [Export download](examples/outputs/data_export_download_run_file.json)
- [Original plan](examples/plan.example.json) and [receipt](examples/receipt.example.json). Create a new plan for an actual change.
