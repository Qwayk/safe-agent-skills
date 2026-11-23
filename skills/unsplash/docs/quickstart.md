# Find and review Unsplash photos

Use [the setup guide](onboarding.md) to connect your Access Key. If you are installing the command from a local copy, use Python 3.11 or newer and run these commands from the package folder.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install .
```

## Search for photos

```bash
unsplash-api-tool auth check
unsplash-api-tool search photos --query "minimal home office" --per-page 10
unsplash-api-tool photos get --id PHOTO_ID
```

Replace `PHOTO_ID` with a result you want to check. For a shortlist, ask the agent to show the photo links, photographer credits, and why each option fits. You can also ask it to find a set of images in one style, compare two collections, or look up a photographer's other work.

Use the image links Unsplash returns when showing previews. Credit the photographer and Unsplash as required for API displays. [Unsplash API guidelines](references.md)

## Save search results for review

```bash
unsplash-api-tool export photos-search --query "minimal home office" --out photos.json
```

An export saves result data on your machine. It does not record a download for the photos in the list. For more than one page, choose `--max-pages` and add the shared `--yes` flag before `export`.

## Download an approved photo

Save a preview with the photo and its destination.

```bash
unsplash-api-tool --plan-out photo-plan.json photos download --id PHOTO_ID --dest downloads/photo.jpg
```

Review the photo, connection, destination, and whether the file will replace an existing one. The tool cannot undo the record Unsplash makes. After approval, apply with the same settings.

```bash
unsplash-api-tool --apply --ack-no-snapshot --plan-in photo-plan.json photos download --id PHOTO_ID --dest downloads/photo.jpg
```

To mark a photo as used without saving a local copy, leave out `--dest` in both commands. For an intentional replacement, use `--overwrite` in the preview and apply, and add `--yes` when applying.

See [what to check after a download](safety_model.md#check-the-result) and [all command options](command_reference.md).
