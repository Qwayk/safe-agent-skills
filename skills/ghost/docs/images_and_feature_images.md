# Images and feature images

Ghost image uploads use:
- `POST /admin/images/upload/` (multipart form-data)

The upload response contains a URL that can be stored in:
- `post.feature_image`
- `post.feature_image_alt`
- `post.feature_image_caption`
- `page.feature_image`
- `page.feature_image_alt`
- `page.feature_image_caption`

Upload fields:
- `file` (required)
- `purpose` (default `image`)
- `ref` (optional, used for tracking)

## Posts

Use:

```bash
ghost-api-tool post set-feature-image --slug SLUG --file path.jpg
ghost-api-tool --apply post set-feature-image --slug SLUG --file path.jpg --alt "..." --caption "..."
```

If the body already contains a suitable Ghost-hosted image, you can set it as the feature image **without uploading**:

```bash
ghost-api-tool post set-feature-from-body --slug SLUG --nth 1
ghost-api-tool --apply post set-feature-from-body --slug SLUG --nth 1 --require-current draft \
  --alt "..." --caption "..."
```

To control the filename used in Ghost storage (and therefore the URL path), pass `--upload-name`:

```bash
ghost-api-tool image upload --file local.jpg --upload-name roasted-turkey-ingredients.jpg
ghost-api-tool --apply post set-feature-image --slug SLUG --file local.jpg --upload-name roasted-turkey-featured.jpg --alt "..." --caption "..."
```

Standalone `image upload` needs plan-first review. If no useful before-state can be saved, apply needs explicit no-snapshot approval where supported, or a clear blocker reason when the tool cannot execute safely.

## Pages

Use:

```bash
ghost-api-tool page set-feature-image --slug SLUG --file path.jpg
ghost-api-tool --apply page set-feature-image --slug SLUG --file path.jpg --alt "..." --caption "..."
```
