# Changelog

This tool uses Semantic Versioning. Before version 1.0, a minor release can include changes to how commands work.

## Unreleased

- Imports and bulk writes now require a saved preview. Saved plans for all writes are checked against the connection and what the command will send.
- Import receipts distinguish a job HubSpot accepted from one that finished. They include commands to check progress and errors. Bulk receipts show partial failures.
- Onboarding keeps the settings file you chose and recognizes tokens already configured in the shell, settings file, or stored OAuth file.
- Merged setup, approval, and developer notes into the pages that already cover them.

## Earlier work

- Added the HubSpot CLI, private app setup, and the agent skill. Removed the starter demo and jobs commands.
- Added `before_state` to previews and required explicit approval for live writes without a saved copy of the old data.
- Made JSON argument errors return one JSON object.
- Documented the commands and recorded the original local checks. See [verification history](docs/proof.md).
