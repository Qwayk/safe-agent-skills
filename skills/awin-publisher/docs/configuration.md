# Configuration

Awin Publisher configuration is the local setup an agent needs before it can review publisher accounts, advertiser programs, links, transactions, and performance data. Put private values in `.env` or the `--env-file` you choose, and keep them out of chat and Git.

Start with the required values below. Add optional settings only when you need to change the API root, timeout, token storage, or safety behavior.

A good first configuration check is: "Show me which Awin Publisher values are required, which ones are optional, and confirm the setup without showing secrets."

## Files

- `.env.example`: copy this to `.env` and keep `.env` local-only.
- `.state/runs/`: optional local history and write proof for write-capable commands.

## Environment variables

- `AWIN_API_TOKEN`: required for the main publisher API command families.
- `AWIN_PROOF_OF_PURCHASE_API_KEY`: required only for `proof-of-purchase orders create`, and only useful after the official publisher and advertiser enablement steps are in place.
- `AWIN_FEED_API_KEY`: required only for `feeds legacy-list` and `feeds legacy-download --feed-id ...`.
- `AWIN_TIMEOUT_S`: optional request timeout in seconds. Default `30`.

## OS environment override

Shell environment values override values loaded from `.env`.
