# What Statuspage reads

The CLI sends `GET` requests to [four public Statuspage routes](api_coverage.md). It can check what a vendor posted on its public page.

In JSON mode, the CLI prints one object. `ok: true` means the read succeeded. The actual service status is in `data.status` when the command includes it. A successful read can report a major outage.

An empty list means the page returned no records for that list. A missing or invalid required field returns `ok: false` and an error. If the page leaves out component details, say those details are unavailable. Include the source page and check time so the reader can compare the result with the page.
