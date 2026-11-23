# Download approvals and errors

Search, preview, and compare photos before choosing one to use. Saving a download preview reads the photo details from Unsplash and writes a local plan. The download count changes only when Unsplash receives and accepts the approved tracking request.

## Before a download

1. Use `--plan-out` to save a preview. Review the photo, the connection, the destination, and any replacement of an existing file.
2. After approval, run the same command with `--plan-in`, `--apply` and `--ack-no-snapshot`. The last flag confirms that the tool cannot restore the old download count. Applying an overwrite also needs `--yes`.
3. If you change the photo, Access Key, API host, destination or overwrite choice, save a new preview. Old previews also need to be saved again.

The preview can include the photographer and the links for showing the image. On apply, the tool checks the destination and sends the tracking link from the preview once. For a local copy, it fetches the full-size image from the photo details and checks the transfer before putting the file at the destination.

## Check the result

- **`not_sent`** means the tracking request did not run. Read and fix the refusal before applying again.
- **`recorded`** means Unsplash accepted tracking. Check separately whether the file was saved. A completed file result includes its length and SHA-256 hash. If an overwrite was interrupted before the file was saved, the original stays in place.
- **`failed`** means Unsplash declined the tracking request.
- **`unknown`** means the tool did not get a reply it could use to confirm tracking. Check before trying again so you do not count the same download twice.

When a receipt is saved, it records tracking, the photo links and photographer details, and any file saved. Read the JSON result if the receipt could not be written. Use `runs list` or `runs show` to find saved run details. The tool cannot undo a count already recorded by Unsplash.

## Files outside the download flow

`onboarding` can create a settings file. `auth key set` saves a private key. An `export` saves local JSON and `--plan-out` saves a preview. Check the path before asking the agent to save any of these files.
