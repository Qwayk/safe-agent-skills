# Recipe workflow (Freepik)

This is the **recipe-only** workflow for finding **non‑AI** stock photos and (when possible) getting **multiple angles from the same photoshoot**.

Important: “same photoshoot” is ultimately a **visual/manual** determination. The API sometimes provides no “series” grouping, and `suggested` is not proof of same shoot.

## Summary

1) Search photos (`filters[content_type][]=photo`)
2) Save previews from search results (`image.source.url`) and shortlist by eye
3) Verify non‑AI by `resource get` + by eye (migration rule: fail-closed; missing/unknown flags are rejected)
4) Use `resource get` to look for “similar” candidates (`same_series` when present, else `suggested`)
5) (Optional) Save extra previews and re-shortlist
6) Prepare dry-run download plans for final picks. apply requires explicit no-snapshot approval before licensed download when no saved snapshot is available.

## Project integrations (optional)

Some projects build additional scripts to:
- run multiple queries per post
- save local preview contact sheets
- collect human approvals
- build batch plans for approved IDs

Keep any project-specific automation inside your project folder (not inside this tool repo).

## Commands (examples)

### Clean shortlist (recommended)

```bash
freepik-api-tool search images --query "lychee martini" --limit 20 \
  --param 'filters[content_type][]=photo' \
  --exclude-ai
```

This is slow because it fetches resource detail for every item to filter AI best‑effort.

### Preferred preview flow (fast + low API calls)

The search response already includes a CDN image URL at `image.source.url`. You can download that URL as a **preview** without doing a `resource get` per item.

Recommended approach:
1) `search images` (photos only)
2) download previews from `image.source.url`
3) visually shortlist 1–3 IDs
4) run `resource get` for the shortlist to confirm `is_ai_generated/has_prompt` and still verify by eye

### Shortlist-first (recommended default)

```bash
freepik-api-tool search images --query "lentil vegetable soup bowl" --limit 50 \
  --param 'filters[content_type][]=photo'

# Then verify candidates one-by-one:
freepik-api-tool resource get --id <ID>
freepik-api-tool preview --id <ID> --save-preview <PREVIEWS_DIR>/<post_slug>  # optional (costlier)
```

### Fast pick-one (fewer calls; stop early)

```bash
freepik-api-tool search images --query "lychee martini" --limit 20 \
  --param 'filters[content_type][]=photo'

# Then check candidates one-by-one:
freepik-api-tool resource get --id <ID>
freepik-api-tool preview --id <ID> --save-preview <PREVIEWS_DIR>
```

### “Discover similar” (same photoshoot)

```bash
freepik-api-tool resource get --id <WINNER_ID>
```

Then look at:
- `data.related_resources.same_series` (best, when present)
- `data.related_resources.suggested` (fallback; mixed and optional)

If the exact sibling image isn’t present in the winner’s series list, pick one item from the series and check *its* series list (multi-hop).

### Download + inventory (always dry-run first)

```bash
freepik-api-tool download --id <ID> --format jpg \
  --out-dir <DOWNLOADS_DIR>/by-post/<post_slug> \
  --inventory <INVENTORY_CSV>

freepik-api-tool --apply download --id <ID> --format jpg \
  --out-dir <DOWNLOADS_DIR>/by-post/<post_slug> \
  --inventory <INVENTORY_CSV>
```

Without explicit no-snapshot approval, apply refuses before the Freepik download/license endpoint, binary fetch, or inventory write. Approved applies must record the no-snapshot limit in the receipt.
