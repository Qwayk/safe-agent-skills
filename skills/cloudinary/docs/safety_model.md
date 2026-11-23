# Approve and check changes

Read an asset or list a folder before deciding what to change. Writes make a preview first.

## Before sending a change

1. Run the write with `--plan-out PATH` to save its preview.
2. Review the Cloudinary library or account, exact target, fields, and upload file. Signed uploads set `overwrite=false` unless you explicitly ask to replace the existing asset.
3. Check recovery. The tool saves no copy of the previous state for a write. Approve that limit before using `--ack-no-snapshot`. Deletes, including the Upload API's destroy commands, intentional replacements, and access-key changes need `--ack-irreversible` too.
4. After approval, run the same request with `--apply --yes --plan-in PATH` and the required acknowledgement flags. Use `--receipt-out PATH` if you want to choose where the receipt goes.

When the target, request fields, or upload contents change, save and review a new preview. Plans from the earlier version also need a new preview.

## After sending a change

Check the receipt before saying the change is done. It shows whether Cloudinary replied and whether the follow-up confirmed the requested result. A denied or failed follow-up leaves the result unconfirmed. If the outcome is unclear, check the current state before retrying.

Keep private results, including access keys and live stream credentials, in the file named by `--out` inside `--project-dir`. Cloudinary backup downloads also use `--out`. Use `--overwrite` only when you intend to replace that local output file.

Use `runs list` and `runs show --run-id ID` to find local run records. By default they are under `.state/runs/` next to the settings file. Keep plans, receipts and output files private when they contain account or media details.

## Backups and published media

Download a backed-up version with `operations upload download-backup`. This is a read. Restore and delete-backup commands are separate writes and need their own reviewed plans.

A file removed from the library can still appear through a cached link. If an approved change also needs cached copies cleared, check Cloudinary's options and verify the link separately. [Cloudinary's cache guide](https://cloudinary.com/documentation/invalidate_cached_media_assets_on_the_cdn)
