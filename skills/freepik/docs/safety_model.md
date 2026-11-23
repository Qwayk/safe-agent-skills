# Download approvals and errors

Search and preview can use API calls. A licensed download can also use credits and add a license or download record to your Freepik account. The tool cannot undo that record or save a restore point for it.

## Before a licensed download

1. Review the image and save the planned download with `--plan-out`. This checks the asset details and writes the preview JSON file.
2. Approve the exact asset IDs, account, format or size, destination, and any overwrite or repeat download. Approve running without a restore point.
3. Apply with `--plan-in`, `--apply` and `--ack-no-snapshot`. A batch also needs `--yes`. The tool compares the effective request with your saved preview and checks the asset details again.

Search with `--exclude-ai` and all licensed downloads require both `is_ai_generated=false` and `has_prompt=false`. Missing or unclear values exclude the asset. Use the preview to judge whether the image itself works for your project.

The tool blocks a repeat asset and format in the inventory and protects existing files unless you approve `--force`. A preview reports `before_state.status=no_snapshot_available`. Keep your saved preview private and review a new one whenever the request changes.

## When a download stops

- `provider_status=outcome_unknown` means the tool could not confirm the answer to the license request. Check Stock downloads in your account before trying again. The tool sends the licensing request once and will not switch to another download endpoint after an error.
- `provider_status=replied` means Freepik replied. Check the returned license link or download ID, if supplied, and any paths in `file_paths`. The tool lists the rows it recorded in `rows`. A file saved just before a CSV error can appear in `file_paths` without an inventory row.
- A batch stops at the first failed download. It keeps earlier files and inventory rows and reports how many rows are left. Check the failed row before preparing a new preview for any remaining work.

For a completed download, the CSV records the saved file, its format, its SHA-256 hash and the license link. The tool can retry fetching bytes from a URL it already received. Any local cleanup is manual. Keep the inventory as your license record.

## Files you can save while reviewing

`--write-jobs` saves a local CSV of candidates. `preview --save-preview` saves a preview image. Use those files to review options before approving a licensed copy.
