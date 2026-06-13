# Connect your Awin Advertiser account

Awin Advertiser needs a local API token and advertiser ID before an agent can inspect publishers, transactions, offers, or product-feed work.

Keep the setup files private. Do not paste `.env` values, API keys, client secrets, OAuth files, or saved token files into chat.

After setup, start with a small account or transaction read before asking for validation or feed work.

## What these fields mean

- `AWIN_API_BASE_URL`: the Awin API host. Most users should keep the default `https://api.awin.com`.
- `AWIN_API_TOKEN`: the token used for normal advertiser reads and writes in this skill.
- `AWIN_ADVERTISER_ID`: the advertiser account ID the tool should query or update.
- `AWIN_API_TIMEOUT_S`: optional timeout in seconds if you want a different network timeout.

Conversion orders use the same `AWIN_API_TOKEN`, but the official endpoint expects it in a different auth header under the hood. You do not need a second secret just to start normal advertiser work here.

## What to ask your agent

- "Help me set up the Awin Advertiser skill and tell me exactly what information I still need."
- "Check whether my Awin token is connected correctly before we review any data."
- "I want to review publisher performance for this advertiser. Start with the safest first step."
- "Prepare a dry-run for a transaction batch validation file and stop before apply."
- "Show me how to upload a product feed safely without making the change yet."
