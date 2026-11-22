# Meta Ads test results

## November 22, 2026 local checks

Both local copies passed 45 tests from the checkout and a fresh install. The downloads include the skill, a blank settings example, the guides, and the presets. Setup creates the selected settings file and prints the account check for that file.

The tests used simulated replies. The comparison asked for both chosen date ranges. The placement export kept two rows for the same ad and date, with $12 and $15 in spend. An export that stopped at a limit reported that it was incomplete. A missing data list returned an error, and an empty list remained a valid result. The tests used no live Meta account requests.

The default is Marketing API v25.0. [Meta’s schedule](https://developers.facebook.com/docs/graph-api/changelog/versions/#marketing-api) lists v24.0 as expired for Marketing API use. The remaining code checks report four existing Ruff warnings and 44 existing type findings.

## March 1, 2026 record

The March 1 UTC check used local tests and sample output. The record noted that it had no live Meta credentials. The saved files show the earlier output format.

- [Version](examples/outputs/version.json) and [account check](examples/outputs/auth_check.json)
- [Account pages](examples/outputs/ad_accounts_list_paginated.json)
- [Insights report](examples/outputs/insights_get.json) and [date comparison](examples/outputs/insights_compare.json)
- [Preset list](examples/outputs/presets_list.json) and [preset details](examples/outputs/presets_show.json)
- [Snapshot export](examples/outputs/snapshot_export.json)
- [Creative anatomy](examples/outputs/creatives_anatomy.json) and [preview](examples/outputs/previews_get.json)

The [Quickstart](quickstart.md) and [export guide](snapshot_export.md) have the current account and reporting commands.
