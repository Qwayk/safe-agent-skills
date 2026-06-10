# Jobs and batches

Batch runs use:

```bash
ghost-api-tool jobs run --file jobs.csv
```

Safety:
- Dry-run by default.
- Live apply for `jobs run` requires explicit no-snapshot approval for mixed row writes that cannot save before-state.
- Stops on the first error by default.
- Returns a single JSON object with per-row results.
- Exits non-zero if any row fails.

## jobs.csv format

Must include `action` and a selector column (`slug` or `id`).

Supported `action` values:
- `post.patch` (`file=patch.json`)
- `post.set-status` (`to=draft|published|scheduled`)
- `post.body.set-captions` (`captions_file=map.json`)

Note:
- Member imports are handled via `ghost-api-tool member import --csv members.csv` (separate command; dry-run by default; live apply is also blocked there when no saved snapshot is available).
