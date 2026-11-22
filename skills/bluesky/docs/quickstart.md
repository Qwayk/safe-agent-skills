# Start using Bluesky

## Install

Use Python 3.12 or later. From the Bluesky tool folder, install it in your Python environment.

```bash
python -m pip install .
bluesky-safe-cli --output json --version
```

## Read public posts

Ask for the latest posts from a handle. Replace the example handle with the one you want.

```bash
bluesky-safe-cli --output json --live api app-bsky-feed-get-author-feed --query actor=sample.bsky.social --query limit=5
```

The posts are in `receipt.response.body.body_json.feed`. If that response includes a `cursor`, pass it as `--query cursor=...` to get the next page. You can also read a public profile with `app-bsky-actor-get-profile` and the same `actor` field, or find feed, graph and moderation commands in the [command list](api_coverage.md).

## Publish a post

[Sign in](onboarding.md) and use the DID shown by `auth check`. A DID is the account's stable ID. Save the post in `post.json` and replace the example DID, text and time.

```json
{
  "repo": "did:plc:your-account",
  "collection": "app.bsky.feed.post",
  "record": {
    "$type": "app.bsky.feed.post",
    "text": "Example post",
    "createdAt": "2026-11-23T05:00:00Z"
  }
}
```

Save the preview. Review the account, server, text and the rest of the post before approving it.

```bash
bluesky-safe-cli --output json --plan-out post-plan.json api com-atproto-repo-create-record --body-json post.json
```

After approval, use the same post file and the reviewed plan. Include `--ack-no-snapshot` to approve sending the post without a saved copy of the previous state.

```bash
bluesky-safe-cli --output json --live --apply --ack-no-snapshot --plan-in post-plan.json --receipt-out post-receipt.json api com-atproto-repo-create-record --body-json post.json
```

Find `uri` and `cid` under `response.body.body_json` in the saved receipt. The URI ends with the record key. Use the DID and key from that URI to read the post back.

```bash
bluesky-safe-cli --output json --live api com-atproto-repo-get-record --query repo=did:plc:your-account --query collection=app.bsky.feed.post --query rkey=the-record-key
```

Compare the returned `cid` and text with the receipt and the reviewed post. If the write times out, check whether the post appeared before trying again. Keep the plan and receipt private when they contain account or post details.
