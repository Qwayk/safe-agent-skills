# Authentication

Klaviyo authentication is meant to be local and boring: put the required key or token in your `.env` file, keep it out of chat, and run the safe check before asking an agent for real account data.

That matters because profiles, lists, segments, campaigns, flows, templates, and events can contain account or business data. The auth check should prove the credential works without printing the secret value.

A good first auth check is: "Confirm the required Klaviyo environment values are present, run the safe auth check, and tell me whether the credential works without showing the secret."

## Setup details

- `KLAVIYO_API_KEY`: used for `Authorization: Klaviyo-API-Key ...` on live calls.
- `KLAVIYO_COMPANY_ID`: optional, used for `/client/*` endpoints.

Run once to verify:

```bash
klaviyo-safe-agent-cli auth check
```

The check does not print secrets.
