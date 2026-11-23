# Search and download stock photos

If you have a local copy of the tool, install it from its folder with Python 3.12 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install .
```

## Find a photo

[Connect your account](onboarding.md), then check the key and run a small search.

```bash
freepik-api-tool auth check
freepik-api-tool search photos --query "mushroom pasta" --limit 10 --exclude-ai --shortlist
freepik-api-tool resource get --id RESOURCE_ID
freepik-api-tool preview --id RESOURCE_ID
```

Replace `RESOURCE_ID` with an actual result. Review the preview before choosing it. To find more angles, try `resource shoot-pack --id RESOURCE_ID` and compare the previews by eye.

## Download one approved asset

Save a preview to a new file. Review the asset ID, account, format or size, and destination. Make sure you approve the possible credit use and understand that the tool cannot undo the license.

```bash
freepik-api-tool --plan-out photo-plan.json download --id RESOURCE_ID --format jpg --out-dir downloads
```

After approval, use the same settings and pass the saved preview.

```bash
freepik-api-tool --plan-in photo-plan.json --apply --ack-no-snapshot download --id RESOURCE_ID --format jpg --out-dir downloads
```

Check the result for the saved file, its SHA-256 hash and the license link. See [what to check if the download stops](safety_model.md#when-a-download-stops).

## Download an approved list

Build a `jobs.csv` with the final picks. The two required columns are `resource_id,format`. You can start from a search made with `--write-jobs candidates.csv` and keep only your chosen rows in `jobs.csv`.

```bash
freepik-api-tool --plan-out batch-plan.json jobs run --file jobs.csv --out-dir downloads
```

Review every row with the same approval as a single download. Use the command below after approval.

```bash
freepik-api-tool --plan-in batch-plan.json --apply --yes --ack-no-snapshot jobs run --file jobs.csv --out-dir downloads
```

If you change the picks, size, format, destination or account, save a new preview and review it before sending another download request.
