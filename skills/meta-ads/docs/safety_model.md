# Read a Meta Ads report

This CLI sends GET requests to read Meta Ads data. Exports and optional creative downloads write files on your machine.

Include the ad account, date range, report level, metrics, and any splits such as placement or age. Compare periods using the same settings. If the report says it stopped at a page or item limit, tell the reader which part is incomplete. A missing row means you lack a result for that row. A reported zero and an empty list are separate results.

For snapshots, open `manifest.json` first. It records the tables, failed requests, and requests that stopped early. Use the full row keys in the manifest when joining results. The [export guide](snapshot_export.md) shows where to find them.

Keep Meta tokens out of shared text and files. The Graph client follows page links on the configured API host. Treat preview HTML as untrusted content and use an isolated viewer if it needs to be rendered.
