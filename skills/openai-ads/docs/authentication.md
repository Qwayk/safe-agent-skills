# Authentication

The Advertiser API uses bearer-token auth with an Ads Manager API key.

```bash
OPENAI_ADS_API_KEY=...
```

The default API base URL is:

```bash
https://api.ads.openai.com/v1
```

Server-side conversion events use a Pixel ID and a Conversions API key:

```bash
OPENAI_ADS_PIXEL_ID=...
OPENAI_ADS_CONVERSIONS_API_KEY=...
OPENAI_ADS_CONVERSIONS_BASE_URL=https://bzr.openai.com/v1
```

Run:

```bash
openai-ads-safe-agent-cli auth check
```

The command calls `GET /ad_account` and never prints the API key.
