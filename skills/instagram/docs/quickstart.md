# Start using Instagram

Use Python 3.12 or later. From the Instagram tool folder, install the tool and [connect your account](onboarding.md).

```bash
python -m pip install .
instagram-api-tool --output json --version
```

## Read your latest posts

```bash
instagram-api-tool auth check
instagram-api-tool media list --fields id,caption,media_type,permalink --limit 5
```

The first command shows the professional account ID and username. The list uses the connected account unless you set a default ID or pass `--ig-user-id`. Posts are in `result.data`. If the response has a `result.paging.cursors.after` value, pass it with `--after` to see the next page.

Use a post ID with `comments list --media-id` to read comments. Use the [command reference](command_reference.md) to find account insights, mentions or other reads.

## Review and publish an image

Use the professional account ID from `auth check` as `ACCOUNT_ID`. Replace the example URL with an image Instagram can download. Save a plan with the exact caption and image.

```bash
instagram-api-tool --plan-out image-plan.json media create-container --ig-user-id ACCOUNT_ID --image-url https://example.invalid/image.jpg --caption 'Example caption'
```

After approving the plan, create the draft. The approval flag allows creating it without a saved copy of the previous state.

```bash
instagram-api-tool --apply --ack-no-snapshot --plan-in image-plan.json media create-container --ig-user-id ACCOUNT_ID --image-url https://example.invalid/image.jpg --caption 'Example caption'
```

Use `receipt.write_result.id` as `DRAFT_ID`. Check the draft status. When Instagram reports it is ready, save the publishing plan.

```bash
instagram-api-tool media container get --container-id DRAFT_ID
instagram-api-tool --plan-out publish-plan.json media publish --ig-user-id ACCOUNT_ID --creation-id DRAFT_ID
```

After approving the publishing plan, apply it and check the receipt. The tool reads the new post by ID when Instagram returns one.

```bash
instagram-api-tool --apply --yes --ack-no-snapshot --plan-in publish-plan.json media publish --ig-user-id ACCOUNT_ID --creation-id DRAFT_ID
```

For a carousel, prepare each image or video with `--is-carousel-item` and its own reviewed plan. Once the pieces are ready, use their IDs together with `--media-type CAROUSEL --children ID1,ID2` and save a plan for the whole carousel. Publish the resulting carousel draft after review. [Meta’s publishing guide](https://developers.facebook.com/documentation/instagram-platform/content-publishing)
