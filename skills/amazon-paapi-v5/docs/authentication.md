# Authentication

Amazon Product Advertising API authentication is meant to be local and checked before an agent works with product lookup and browse-node research. Keep credentials local, run the safe check first, and do not paste secrets into chat.

The goal is simple: prove the tool can reach the right account without exposing private values or making a live change.

A good first auth check is: "Check the Amazon Product Advertising API credential setup, run the safe auth check, and stop before any account change."

## Authentication notes

Amazon PA-API v5 uses AWS-style credentials + your Associates tracking ID.

Put your keys in `.env` (gitignored) and validate with:

## Setup details

```bash
amazon-pa-api-tool auth check
```

Important:
- Never paste keys into chat/logs.
- Never print `Authorization` headers (this tool does not).
