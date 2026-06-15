# Troubleshooting

When Skimlinks stops or returns an error, start with the boring checks first: setup, account access, target IDs, API limits, and the tool's safety gates. That usually tells you whether the problem is local configuration, provider permissions, a bad request, or a write that correctly refused to run.

Keep the JSON error output. It is the best clue for an agent reviewing merchants, links, performance, and affiliate reporting, and it is safer than retrying commands blindly. For any write-related error, stop before retrying and confirm the needed approval or plan.

A good first troubleshooting ask is: "Read the Skimlinks error, explain what failed in plain English, tell me the safest next check, and do not retry any write or destructive action."

## Missing Config

Run:

```bash
skimlinks-safe-cli onboarding
```

Then fill `.env` locally. Do not paste secrets into chat.

## Auth Fails

Run:

```bash
skimlinks-safe-cli auth check --scope all
```

If shared auth fails, check `SKIMLINKS_CLIENT_ID` and `SKIMLINKS_CLIENT_SECRET`.

If Product Key fails, ask Skimlinks to enable Product Key credentials for your account.

If Product Key says the publisher domain ID is missing, set `SKIMLINKS_PUBLISHER_DOMAIN_ID` or pass `--publisher-domain-id`.

## Link Wrapper ID Missing

Set `SKIMLINKS_LINK_WRAPPER_ID` or pass `--id` to `link-wrapper build`.

## Debug Mode

Use `--verbose` for request start/end lines. The tool redacts token-style query values.

Use `--debug` only for local development when you need a Python stack trace.
