# Troubleshooting

When Ghost stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing posts, pages, members, tags, and publication data, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Ghost error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## “Missing GHOST_ADMIN_API_URL”

Create `.env` from `.env.example`.

## HTTP errors

Run with `--verbose` to see request start/end lines:

```bash
ghost-api-tool --verbose auth check
```

Network exceptions always include `METHOD + URL`.

## Verification failed after update

This means Ghost returned a response but the fields you asked to change did not match after re-fetch.
Re-run the command without `--apply` to inspect the planned change, then check whether Ghost is transforming the content (common with HTML-to-Lexical conversion).

## Bodylex refused / ambiguous selector

Common refusal reasons and fixes:

- “heading matched multiple times … pass --heading-occurrence”: run `ghost-api-tool post bodylex inspect --slug SLUG` and choose which heading occurrence to target.
- “No image found after heading …”: confirm the heading text matches exactly (case-insensitive, whitespace-normalized) and adjust `--nth-after-heading`.
- “post status is published/scheduled; pass --allow-published”: either add `--allow-published` or (recommended) edit drafts and use `--require-current draft`.

## Bodylex verification failed (idempotence)

If a `post bodylex ...` command applies but then fails verification, it means re-running the same transform would still change the post.
Run the same command without `--apply --diff` and inspect the diff to see what Ghost is normalizing.

## Audit shows “WordPress uploads”

This means the post body still contains image URLs pointing at the old WordPress site (commonly `/wp-content/uploads/...`).
The typical fix is:
- download the image from WordPress (or by URL)
- upload to Ghost with a good filename
- replace the body image `src` in Lexical and set `alt`/`caption`

## Debug errors

By default the tool prints a single JSON error message.
If you want the full Python stack trace (developer debugging), add `--debug`.
