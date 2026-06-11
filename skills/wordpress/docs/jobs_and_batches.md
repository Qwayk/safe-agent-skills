# Jobs and batches

Jobs let you apply many small, safe operations from a file.

## Safety

Batch writes require:
- `--apply`
- `--yes`

Batch jobs stop on the **first error** by default and return a non-zero exit code during dry-run evaluation.

Write mode is currently blocked for `jobs run` in this release. Use dry-run output to review and then run each row directly
with single-write commands.

## JSON format

Either:
- a list of job objects, or
- an object with `{"jobs": [...]}`.

Example:

```json
{
  "jobs": [
    {"action": "media.set", "id": 123, "caption": "Photo: ..."},
    {"action": "post.set_image_captions", "slug": "my-post", "caption": "Photo: ...", "diff": true}
  ]
}
```

## CSV format

Must include an `action` column.

Example columns:
- `action`
- `id` (for `media.set`)
- `slug`, `post_type`, `caption`, `caption_html`, `captions_file`, `alt_text`, `only_ids` (for `post.set_image_captions`)

Optional:
- `diff` (for `post.set_image_captions`): set to `true`/`1` to include a unified diff in output (off by default for jobs).
