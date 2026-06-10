# Content handling

## Captions live in two places in WordPress

1) **Media Library caption** (attachment metadata): updated with `media set`.
2) **Caption shown inside the post** (`<figcaption>` in Gutenberg blocks): updated with `post set-image-captions`.

## Strict policy (no guessing)

`post set-image-captions` only edits Gutenberg `wp:image` blocks where it can confidently determine the attachment id:
- JSON attrs include an integer `id`, or
- the block HTML contains an `<img>` with a `wp-image-<id>` class.
If the post uses another structure, the tool refuses and explains why.

## What this means in practice

- Works best when images were inserted using the WordPress block editor (Image block).
- If your post contains images inside:
  - a Custom HTML block
  - shortcodes
  - theme-specific markup without an attachment id
  then the tool will usually refuse to edit post-body captions (because it can’t be sure which image is which).

In those cases, you can still often use `media set` to update the Media Library caption/alt/title by attachment id.

## Faster edits for many images (still safe)

If you need **different captions per image** in a single post, use `--captions-file` so the tool updates the post only once:

- `wordpress-api-tool post set-image-captions --slug SLUG --captions-file captions.json`
- `wordpress-api-tool --apply post set-image-captions --slug SLUG --captions-file captions.json`

`captions.json` can be either:
- an object mapping id to caption: `{"2264": "Caption ...", "2266": "Caption ..."}`
- or a list: `[{"id": 2264, "caption": "Caption ..."}, ...]`
