# Authentication

Amazon PA-API v5 uses AWS-style credentials + your Associates tracking ID.

Put your keys in `.env` (gitignored) and validate with:

```bash
amazon-pa-api-tool auth check
```

Important:
- Never paste keys into chat/logs.
- Never print `Authorization` headers (this tool does not).
