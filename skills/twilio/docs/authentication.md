# Twilio authentication

## Preferred: API key Basic authentication

Most pinned operations use HTTP Basic authentication. Configure the Account SID, API key SID, and API key secret:

```dotenv
TWILIO_ACCOUNT_SID=AC...
TWILIO_API_KEY_SID=SK...
TWILIO_API_KEY_SECRET=...
```

Use a Restricted API key when its permissions cover the intended commands. A Restricted key can be scoped, and any API key can be revoked without rotating the Account Auth Token.

## Warned fallback: Account Auth Token

If an operation cannot use the preferred key, set:

```dotenv
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
```

The tool authenticates with the Account SID and Auth Token and adds a warning to the public auth summary. Do not make this the normal production setup.

## Operation-scoped OAuth

Only commands whose pinned specification requires OAuth read `TWILIO_OAUTH_ACCESS_TOKEN`. The token is sent as a Bearer token for that operation; it is not a general fallback for Basic-auth commands.

Some pinned Flex operations declare an `Authorization` input header instead of a normal security scheme. The tool accepts that header only when the operation declares it and warns that live behavior is unverified.

## Regions and edges

Set region and edge together:

```dotenv
TWILIO_REGION=au1
TWILIO_EDGE=sydney
```

Setting only one is refused. The tool inserts the pair into the pinned `twilio.com` hostname and refuses routed hosts outside that boundary. API credentials are region-specific, so use credentials valid for the selected region.

## Check the setup

Local validation does not contact Twilio:

```bash
qwayk-twilio-safe-agent-cli auth check
```

Add `--live` only when you want the safe account fetch:

```bash
qwayk-twilio-safe-agent-cli auth check --live
```

The command reports the auth method and an account fingerprint, never the secret. Never paste `.env`, keys, tokens, Authorization headers, or full sensitive results into chat.

Official guidance is linked in [references](references.md).
