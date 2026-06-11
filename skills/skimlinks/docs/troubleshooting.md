# Troubleshooting

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
