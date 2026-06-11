# Data models

The tool outputs JSON objects with:
- `target`: what will be changed (IDs, slugs)
- `apply`: whether it wrote changes
- `changes`: before/after values
- `verified`: whether the API read-back matches expected values

## Example: `media set` (dry-run)

```json
{
  "apply": false,
  "changes": {
    "caption": {"before": "Old", "after": "New"}
  },
  "target": {"media_id": 123, "source_url": "https://.../image.jpg"}
}
```

## Example: `post set-image-captions` (dry-run)

```json
{
  "apply": false,
  "post": {"id": 999, "slug": "my-post", "post_type": "posts"},
  "report": {"matched_blocks": 3, "updated_blocks": 2, "refused_blocks": 1, "reasons": ["..."], "diff": "--- ..."}
}
```
