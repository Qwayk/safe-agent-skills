# Find stock photos for recipes

Look for non-AI photos of the right dish. If you need several angles, use Freepik's series and related results as leads and compare the previews by eye.

## Find and review photos

```bash
freepik-api-tool search images --query "lychee martini" --limit 20 \
  --param 'filters[content_type][]=photo' --exclude-ai
```

`--exclude-ai` reads the details of every result. To use fewer API calls, run the search without that flag, look through the preview links in `image.source.url`, then check the details of only your finalists.

```bash
freepik-api-tool resource get --id RESOURCE_ID
freepik-api-tool preview --id RESOURCE_ID --save-preview previews/post-slug
```

The optional `--save-preview` puts a local review copy in the folder you choose. Check that the details show `is_ai_generated=false` and `has_prompt=false` for every asset you plan to use.

## Find another angle

In `resource get`, look for `data.related_resources.same_series`. If you see a promising match, open its details and check its series too. You can also check `suggested` for ideas. Compare the dish, props and lighting in the previews before calling two photos part of the same shoot.

## Download after approval

Save a preview for the exact photo and review the account, format and destination.

```bash
freepik-api-tool --plan-out recipe-plan.json download --id RESOURCE_ID --format jpg \
  --out-dir downloads/by-post/post-slug --inventory licensed-downloads-ledger.csv
```

After approval, apply the same request.

```bash
freepik-api-tool --plan-in recipe-plan.json --apply --ack-no-snapshot download \
  --id RESOURCE_ID --format jpg --out-dir downloads/by-post/post-slug \
  --inventory licensed-downloads-ledger.csv
```

Use the [batch example](quickstart.md#download-an-approved-list) for several approved photos. Keep extra queries, contact sheets and project-specific approval scripts with the project that uses them.
