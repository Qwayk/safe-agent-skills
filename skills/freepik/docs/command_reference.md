# Command reference

Put shared flags before the command name.

| Flag | What it does |
| --- | --- |
| `--env-file PATH` | Read a private settings file. Defaults to `.env`. |
| `--config PATH` | Read project paths from a JSON file. |
| `--project-dir DIR` | Set the folder for default download and inventory paths. |
| `--timeout-s SECONDS`, `--accept-language LANG` | Override the connection settings for this run. |
| `--output json\|text` | Choose the output. JSON is the default and prints one object. |
| `--log-file PATH`, `--verbose`, `--debug` | Save an audit log, show request lines, or show Python errors. |
| `--plan-out FILE` | Save a single or batch download preview to a new JSON file. |
| `--plan-in FILE` | Check the saved preview before applying a download. |
| `--apply`, `--ack-no-snapshot`, `--yes` | Apply the approved download, confirm it has no restore point, and confirm a batch if used. |

## Check, search and preview

- `auth check` checks the key with one search.
- `search images --query TEXT` searches images and templates. `search photos --query TEXT` adds the photo filter by default.
- `resource get --id ID` returns the asset detail.
- `resource related --id ID [--limit N]` shows related assets.
- `resource shoot-pack --id ID [--limit N] [--same-series] [--same-collection] [--same-author] [--suggested]` looks for alternatives around one asset. It also accepts the jobs CSV flags below.
- `preview --id ID [--save-preview DIR]` shows a preview URL or saves the preview file.

Both search commands accept `--page N`, `--limit N`, and repeatable `--param KEY=VALUE`. Example filters are `'filters[license][freemium]=1'`, `'filters[license][premium]=1'`, `'filters[orientation]=horizontal'` and `'filters[content_type][]=photo'`. Keep the `[]` on the photo filter because the API expects a list.

`--exclude-ai` reads each result's details and keeps assets with both non-AI flags set to false. It makes extra API calls. `--shortlist` returns `ok`, `mode`, `query`, `page`, `limit`, `count` and `items`. Each item can include `id`, `title`, `preview_url`, `license_url`, `author`, `orientation` and `resource_url`. The `tool` section shows the filter counts when used.

`--write-jobs PATH` saves a local CSV and reports its path, row count and columns in `jobs_csv` with a shortlist. Use `--job-format FMT` to change the default `jpg`, and `--job-image-size SIZE` to set an optional size.

## Single or batch download

- `download --id ID --format FMT` plans one licensed download.
- `jobs run --file jobs.csv [--limit N]` plans the selected CSV rows in order.

Both accept `--out-dir DIR` and `--inventory PATH`. For one download, you can also pass `--image-size SIZE`, `--post-slug SLUG`, `--ghost-id ID`, `--usage-role featured|body`, `--download-url-jsonpath PATH`, `--license-url-jsonpath PATH` and `--force`.

A requested image size uses Freepik's size endpoint. Without a size the tool asks the format endpoint for the format you chose. The file Freepik sends can have a different format. Check the inventory row for what was saved.

For a batch, put the per-download settings in the CSV. Use `resource_id` (or `id`) and `format`. Optional columns are `image_size`, `post_slug`, `ghost_id`, `usage_role`, `force`, `download_url_jsonpath` and `license_url_jsonpath`. The output is one JSON result for the batch.

See [single and batch examples](quickstart.md#download-one-approved-asset) and [what to do after a failed download](safety_model.md#when-a-download-stops).
